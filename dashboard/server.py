#!/usr/bin/env python3
"""
VN Stock Dashboard — FastAPI Backend
Run: source .venv/bin/activate && python dashboard/server.py
"""

from __future__ import annotations
import sys, os, json, datetime as dt, math, re, glob
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

# Add project root so we can import vn_buffett
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

app = FastAPI(title="VN Stock Dashboard", version="1.0.0")

# --- Serve static frontend ---
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# --- Watchlist persistence ---
WATCHLIST_FILE = PROJECT_ROOT / "dashboard" / "watchlist.json"

def _load_watchlist() -> list[str]:
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text())
    return ["VCB", "FPT", "VNM", "HPG", "MWG"]

def _save_watchlist(tickers: list[str]):
    WATCHLIST_FILE.write_text(json.dumps(tickers))


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
    """Fetch live stock overview + ratios via vnstock."""
    ticker = ticker.upper().strip()
    try:
        from vnstock import Vnstock
        stock = Vnstock().stock(symbol=ticker, source="VCI")

        # Overview
        ov = stock.company.overview()
        ov_row = ov.iloc[0].to_dict() if ov is not None and not ov.empty else {}

        # Latest price
        end = dt.date.today()
        start = end - dt.timedelta(days=10)
        px = stock.quote.history(start=start.isoformat(), end=end.isoformat(), interval="1D")
        last_close = None
        prev_close = None
        if px is not None and not px.empty:
            last_close = float(px.iloc[-1]["close"])
            if len(px) >= 2:
                prev_close = float(px.iloc[-2]["close"])

        # Ratios
        ratio_df = stock.finance.ratio(period="year", lang="en")
        latest_ratio = {}
        if ratio_df is not None and not ratio_df.empty:
            ratio_df = ratio_df.sort_index(ascending=False)
            latest_ratio = ratio_df.head(1).to_dict(orient="records")[0]

        def safe(val, default=0.0):
            if val is None: return default
            try:
                fv = float(val)
                return default if (math.isnan(fv) or math.isinf(fv)) else fv
            except: return default

        change = 0
        change_pct = 0
        if last_close and prev_close and prev_close > 0:
            change = last_close - prev_close
            change_pct = (change / prev_close) * 100

        return {
            "ticker": ticker,
            "name": ov_row.get("short_name") or ov_row.get("organ_name") or ticker,
            "industry": ov_row.get("industry") or ov_row.get("icb_name_lv2") or "N/A",
            "exchange": ov_row.get("exchange") or "N/A",
            "last_close": last_close,
            "prev_close": prev_close,
            "change": round(change, 0),
            "change_pct": round(change_pct, 2),
            "pe": safe(latest_ratio.get("price_to_earning")),
            "pb": safe(latest_ratio.get("price_to_book")),
            "roe": round(safe(latest_ratio.get("roe")) * 100, 2),
            "roa": round(safe(latest_ratio.get("roa")) * 100, 2),
            "de": safe(latest_ratio.get("debt_on_equity")),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/buffett/{ticker}")
async def run_buffett(ticker: str):
    """Run Buffett analysis and return structured results."""
    ticker = ticker.upper().strip()
    try:
        import vn_buffett as vb
        is_bank = ticker in vb.BANK_TICKERS
        ratios = vb.fetch_ratios(ticker)
        results, passed = vb.score(ratios, is_bank)
        v_tag, v_reason = vb.verdict(passed, len(results))

        # Save report
        report = vb.render_report(ratios, results, passed, len(results), is_bank)
        out_dir = PROJECT_ROOT / "out"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"buffett-{ticker}-{dt.date.today().isoformat()}.md"
        out_path.write_text(report, encoding="utf-8")

        return {
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
                "pe": ratios.get("pe", 0),
                "pb": ratios.get("pb", 0),
                "roe": round(ratios.get("roe", 0) * 100, 2),
                "roe_3y": round(ratios.get("roe_3y", 0) * 100, 2),
                "roa": round(ratios.get("roa", 0) * 100, 2),
                "de": ratios.get("d_e", 0),
                "eps_cagr_5y": round(ratios.get("eps_cagr_5y", 0) * 100, 2),
                "fcf_pos_3y": ratios.get("fcf_pos_3y", False),
                "last_close": ratios.get("last_close"),
            },
            "report_path": str(out_path),
            "date": dt.date.today().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports")
async def list_reports():
    """List all saved Buffett reports."""
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
    """Read a specific report."""
    out_dir = PROJECT_ROOT / "out"
    filepath = out_dir / filename
    if not filepath.exists() or not filepath.name.startswith("buffett-"):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"content": filepath.read_text(encoding="utf-8"), "filename": filename}


@app.get("/api/market")
async def market_overview():
    """Quick market snapshot."""
    try:
        from vnstock import Vnstock
        stock = Vnstock().stock(symbol="ACB", source="VCI")

        end = dt.date.today()
        start = end - dt.timedelta(days=10)

        indices = {}
        for idx_symbol in ["VNINDEX", "VN30", "HNX"]:
            try:
                s = Vnstock().stock(symbol=idx_symbol, source="VCI")
                px = s.quote.history(start=start.isoformat(), end=end.isoformat(), interval="1D")
                if px is not None and not px.empty:
                    last = float(px.iloc[-1]["close"])
                    prev = float(px.iloc[-2]["close"]) if len(px) >= 2 else last
                    indices[idx_symbol] = {
                        "value": last,
                        "change": round(last - prev, 2),
                        "change_pct": round(((last - prev) / prev) * 100, 2) if prev else 0,
                    }
            except:
                pass

        return {"indices": indices, "date": dt.date.today().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 VN Stock Dashboard starting at http://localhost:8686")
    uvicorn.run(app, host="0.0.0.0", port=8686, log_level="info")
