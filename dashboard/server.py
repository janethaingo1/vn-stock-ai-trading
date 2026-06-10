#!/usr/bin/env python3
"""
VN Stock Dashboard — FastAPI Backend (vnstock v4 API)
Run: source .venv/bin/activate && python dashboard/server.py
"""

from __future__ import annotations
import sys, os, json, datetime as dt, math, re, time, hashlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

app = FastAPI(title="VN Stock Dashboard", version="2.0.0")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ===== SIMPLE IN-MEMORY CACHE (avoids rate limits) =====
_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 300  # 5 minutes

def _get_cached(key: str) -> Optional[dict]:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
    return None

def _set_cache(key: str, data: dict):
    _cache[key] = (time.time(), data)

# ===== RATE LIMITER =====
_last_api_call = 0.0
API_INTERVAL = 3.5  # seconds between vnstock calls

def _rate_wait():
    global _last_api_call
    now = time.time()
    wait = API_INTERVAL - (now - _last_api_call)
    if wait > 0:
        time.sleep(wait)
    _last_api_call = time.time()

# ===== VNSTOCK V4 HELPERS =====
def _safe(val, default=0.0) -> float:
    if val is None: return default
    try:
        fv = float(val)
        return default if (math.isnan(fv) or math.isinf(fv)) else fv
    except (TypeError, ValueError):
        return default

def _get_ratio_value(ratio_df, metric_name: str) -> float:
    """Extract a metric from the pivoted ratio DataFrame.
    vnstock v4 format: rows=metrics (item_en), columns 0-2 are metadata,
    columns 3+ are year/quarter data with DUPLICATE column names.
    The LAST column (iloc[-1]) is the latest period."""
    if ratio_df is None or ratio_df.empty:
        return 0.0
    try:
        # Find the row matching the metric name
        mask = ratio_df['item_en'].str.strip().str.lower() == metric_name.strip().lower()
        if not mask.any():
            # Try partial match
            mask = ratio_df['item_en'].str.contains(metric_name, case=False, na=False, regex=False)
        if not mask.any():
            return 0.0
        row = ratio_df[mask].iloc[0]
        # Data columns start at position 3 (after item, item_en, item_id)
        # The latest value is the LAST column
        for pos in [-1, -2, -3]:
            try:
                val = _safe(row.iloc[pos])
                if val != 0.0:
                    return val
            except IndexError:
                continue
        return 0.0
    except Exception:
        return 0.0


# ===== WATCHLIST =====
WATCHLIST_FILE = PROJECT_ROOT / "dashboard" / "watchlist.json"

def _load_watchlist() -> list[str]:
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text())
    return ["VCB", "FPT", "VNM", "HPG", "MWG"]

def _save_watchlist(tickers: list[str]):
    WATCHLIST_FILE.write_text(json.dumps(tickers))


# ===== BANK TICKERS =====
BANK_TICKERS = {
    "VCB", "BID", "CTG", "TCB", "MBB", "VPB", "ACB", "STB", "SHB",
    "HDB", "TPB", "VIB", "LPB", "OCB", "MSB", "EIB", "NAB", "VAB",
    "BAB", "ABB", "SGB", "KLB", "PGB", "BVB", "NVB",
}


# ===== ROUTES =====

@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/watchlist")
async def get_watchlist():
    return {"tickers": _load_watchlist()}


@app.post("/api/watchlist/add")
async def add_to_watchlist(ticker: str = Query(...)):
    wl = _load_watchlist()
    t = ticker.upper().strip()
    if t not in wl:
        wl.append(t)
        _save_watchlist(wl)
    return {"tickers": wl}


@app.post("/api/watchlist/remove")
async def remove_from_watchlist(ticker: str = Query(...)):
    wl = _load_watchlist()
    t = ticker.upper().strip()
    wl = [x for x in wl if x != t]
    _save_watchlist(wl)
    return {"tickers": wl}


@app.get("/api/stock/{ticker}")
async def get_stock_data(ticker: str):
    """Fetch stock overview + ratios via vnstock v4 API."""
    ticker = ticker.upper().strip()
    cached = _get_cached(f"stock:{ticker}")
    if cached:
        return cached

    try:
        from vnstock.api.quote import Quote
        from vnstock.api.company import Company
        from vnstock.api.financial import Finance

        # Overview (includes current_price, sector, is_bank, etc.)
        _rate_wait()
        c = Company(symbol=ticker, source='VCI')
        ov = c.overview()
        ov_row = ov.iloc[0].to_dict() if ov is not None and not ov.empty else {}

        # Price history
        _rate_wait()
        q = Quote(symbol=ticker, source='VCI')
        end = dt.date.today()
        start = end - dt.timedelta(days=14)
        px = q.history(start=start.isoformat(), end=end.isoformat(), interval='1D')
        last_close = None
        prev_close = None
        if px is not None and not px.empty:
            last_close = float(px.iloc[-1]["close"])
            if len(px) >= 2:
                prev_close = float(px.iloc[-2]["close"])

        # Ratios (pivoted format: rows=metrics, cols=years)
        _rate_wait()
        f = Finance(symbol=ticker, source='VCI')
        ratio_df = f.ratio(period='year', lang='en')

        pe = _get_ratio_value(ratio_df, "P/E")
        pb = _get_ratio_value(ratio_df, "P/B")
        roe = _get_ratio_value(ratio_df, "ROE (%)")
        roa = _get_ratio_value(ratio_df, "ROA (%)")
        de = _get_ratio_value(ratio_df, "Debt to Equity")

        # Use overview current_price if history fails
        if last_close is None:
            last_close = _safe(ov_row.get("current_price"))

        change = 0.0
        change_pct = 0.0
        if last_close and prev_close and prev_close > 0:
            change = last_close - prev_close
            change_pct = (change / prev_close) * 100

        result = {
            "ticker": ticker,
            "name": ov_row.get("organ_short_name") or ov_row.get("organ_name") or ticker,
            "industry": ov_row.get("sector") or "N/A",
            "exchange": ov_row.get("com_group_code") or "N/A",
            "is_bank": ov_row.get("is_bank", ticker in BANK_TICKERS),
            "last_close": last_close,
            "prev_close": prev_close,
            "change": round(change, 0),
            "change_pct": round(change_pct, 2),
            "pe": round(pe, 2),
            "pb": round(pb, 2),
            "roe": round(roe * 100, 2) if roe < 1 else round(roe, 2),
            "roa": round(roa * 100, 2) if roa < 1 else round(roa, 2),
            "de": round(de, 2),
            "rating": ov_row.get("rating"),
            "target_price": _safe(ov_row.get("target_price")),
        }
        _set_cache(f"stock:{ticker}", result)
        return result

    except Exception as e:
        err_msg = str(e).split('\n')[0][:200]
        raise HTTPException(status_code=500, detail=err_msg)


@app.get("/api/buffett/{ticker}")
async def run_buffett(ticker: str):
    """Run Buffett analysis via vn_buffett.py (original script)."""
    ticker = ticker.upper().strip()
    cached = _get_cached(f"buffett:{ticker}")
    if cached:
        return cached

    try:
        # Try using the vn_buffett script directly
        import vn_buffett as vb

        is_bank = ticker in vb.BANK_TICKERS
        ratios = vb.fetch_ratios(ticker)
        results, passed = vb.score(ratios, is_bank)
        v_tag, v_reason = vb.verdict(passed, len(results))

        report = vb.render_report(ratios, results, passed, len(results), is_bank)
        out_dir = PROJECT_ROOT / "out"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"buffett-{ticker}-{dt.date.today().isoformat()}.md"
        out_path.write_text(report, encoding="utf-8")

        result = {
            "ticker": ticker,
            "name": ratios.get("name", ticker),
            "is_bank": is_bank,
            "verdict": v_tag,
            "verdict_reason": v_reason,
            "passed": passed,
            "total": len(results),
            "score_pct": round((passed / len(results)) * 100) if results else 0,
            "criteria": [{"label": label, "passed": p} for label, p in results],
            "ratios": {
                "pe": round(_safe(ratios.get("pe")), 2),
                "pb": round(_safe(ratios.get("pb")), 2),
                "roe": round(_safe(ratios.get("roe")) * 100, 2),
                "roe_3y": round(_safe(ratios.get("roe_3y")) * 100, 2),
                "roa": round(_safe(ratios.get("roa")) * 100, 2),
                "de": round(_safe(ratios.get("d_e")), 2),
                "eps_cagr_5y": round(_safe(ratios.get("eps_cagr_5y")) * 100, 2),
                "fcf_pos_3y": ratios.get("fcf_pos_3y", False),
                "last_close": ratios.get("last_close"),
            },
            "report_path": str(out_path),
            "date": dt.date.today().isoformat(),
        }
        _set_cache(f"buffett:{ticker}", result)
        return result

    except Exception as e:
        err_msg = str(e).split('\n')[0][:200]
        # If vn_buffett fails (e.g. old API), try a lightweight analysis from /api/stock data
        try:
            stock_data = await get_stock_data(ticker)
            is_bank = stock_data.get("is_bank", ticker in BANK_TICKERS)

            # Lightweight Buffett criteria check
            criteria = []
            if is_bank:
                criteria = [
                    ("ROE ≥ 15% (latest)", stock_data.get("roe", 0) >= 15),
                    ("ROA ≥ 1% (latest)", stock_data.get("roa", 0) >= 1),
                    ("P/B ≤ 2.0", 0 < stock_data.get("pb", 99) <= 2.0),
                    ("P/E ≤ 15", 0 < stock_data.get("pe", 99) <= 15),
                ]
            else:
                criteria = [
                    ("ROE ≥ 15% (latest)", stock_data.get("roe", 0) >= 15),
                    ("D/E ≤ 0.5", stock_data.get("de", 99) <= 0.5),
                    ("P/E ≤ 20", 0 < stock_data.get("pe", 99) <= 20),
                    ("P/B ≤ 3.0", 0 < stock_data.get("pb", 99) <= 3.0),
                ]

            passed = sum(1 for _, p in criteria if p)
            total = len(criteria)
            pct = (passed / total * 100) if total else 0

            if pct >= 75: v_tag, v_reason = "BUY", "Meets most Buffett criteria at current valuation."
            elif pct >= 50: v_tag, v_reason = "WATCH", "Some quality, but not all criteria met."
            else: v_tag, v_reason = "PASS", "Does not meet enough Buffett criteria."

            result = {
                "ticker": ticker,
                "name": stock_data.get("name", ticker),
                "is_bank": is_bank,
                "verdict": v_tag,
                "verdict_reason": v_reason + " (Lightweight — vn_buffett.py unavailable)",
                "passed": passed,
                "total": total,
                "score_pct": round(pct),
                "criteria": [{"label": l, "passed": p} for l, p in criteria],
                "ratios": {
                    "pe": stock_data.get("pe", 0),
                    "pb": stock_data.get("pb", 0),
                    "roe": stock_data.get("roe", 0),
                    "roe_3y": stock_data.get("roe", 0),
                    "roa": stock_data.get("roa", 0),
                    "de": stock_data.get("de", 0),
                    "eps_cagr_5y": 0,
                    "fcf_pos_3y": False,
                    "last_close": stock_data.get("last_close"),
                },
                "report_path": None,
                "date": dt.date.today().isoformat(),
            }
            _set_cache(f"buffett:{ticker}", result)
            return result
        except Exception:
            raise HTTPException(status_code=500, detail=err_msg)


@app.get("/api/reports")
async def list_reports():
    out_dir = PROJECT_ROOT / "out"
    if not out_dir.exists():
        return {"reports": []}
    files = sorted(out_dir.glob("buffett-*.md"), reverse=True)
    reports = []
    for f in files[:50]:
        match = re.match(r"buffett-(\w+)-(\d{4}-\d{2}-\d{2})\.md", f.name)
        if match:
            reports.append({
                "ticker": match.group(1),
                "date": match.group(2),
                "filename": f.name,
                "size": f.stat().st_size,
            })
    return {"reports": reports}


@app.get("/api/reports/{filename}")
async def get_report(filename: str):
    out_dir = PROJECT_ROOT / "out"
    filepath = out_dir / filename
    if not filepath.exists() or not filepath.name.startswith("buffett-"):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"content": filepath.read_text(encoding="utf-8"), "filename": filename}


@app.get("/api/market")
async def market_overview():
    cached = _get_cached("market")
    if cached:
        return cached

    try:
        from vnstock.api.quote import Quote

        end = dt.date.today()
        start = end - dt.timedelta(days=14)
        indices = {}

        for idx_symbol in ["VNINDEX", "VN30", "HNX"]:
            try:
                _rate_wait()
                q = Quote(symbol=idx_symbol, source='VCI')
                px = q.history(start=start.isoformat(), end=end.isoformat(), interval='1D')
                if px is not None and not px.empty:
                    last = float(px.iloc[-1]["close"])
                    prev = float(px.iloc[-2]["close"]) if len(px) >= 2 else last
                    indices[idx_symbol] = {
                        "value": last,
                        "change": round(last - prev, 2),
                        "change_pct": round(((last - prev) / prev) * 100, 2) if prev else 0,
                    }
            except Exception:
                pass

        result = {"indices": indices, "date": dt.date.today().isoformat()}
        _set_cache("market", result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cache/clear")
async def clear_cache():
    _cache.clear()
    return {"status": "ok", "message": "Cache cleared"}


if __name__ == "__main__":
    print("🎩 VN Stock Dashboard v2.0")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🌐 http://localhost:8686")
    print("📊 Cache TTL: 5 min | Rate limit: 3.5s between calls")
    print("⏹  Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8686, log_level="info")
