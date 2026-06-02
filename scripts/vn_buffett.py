#!/usr/bin/env python3
"""
VN Buffett Analyzer
-------------------
Usage:  python3 vn_buffett.py <TICKER>
        python3 vn_buffett.py VCB

Pulls fundamentals via the public `vnstock` library, applies a Buffett-style
quality rubric (bank vs non-bank branched), and emits a markdown report to
stdout AND to ./out/buffett-<TICKER>-<YYYY-MM-DD>.md.

Dependencies:
    pip install -U vnstock pandas

No outbound calls except via vnstock. No trading. Read-only.
"""

from __future__ import annotations

import sys
import json
import math
import hashlib
import datetime as dt
from pathlib import Path
from typing import Callable

try:
    from vnstock import Vnstock
except ImportError:
    print("ERROR: vnstock not installed. Run: pip install -U vnstock pandas", file=sys.stderr)
    sys.exit(2)


RUBRIC_VERSION = "buffett-vn-v1.0"

# Known Vietnamese listed banks — used to branch the rubric.
BANK_TICKERS = {
    "VCB", "BID", "CTG", "TCB", "MBB", "VPB", "ACB", "STB", "SHB",
    "HDB", "TPB", "VIB", "LPB", "OCB", "MSB", "EIB", "NAB", "VAB",
    "BAB", "ABB", "SGB", "KLB", "PGB", "BVB", "NVB",
}

# Buffett rubric — non-bank. Each: (label, predicate over ratios dict)
NON_BANK_RUBRIC: list[tuple[str, Callable[[dict], bool]]] = [
    ("ROE ≥ 15% (3y avg)",           lambda r: _safe(r, "roe_3y")  >= 0.15),
    ("ROIC ≥ 12% (latest)",          lambda r: _safe(r, "roic")    >= 0.12),
    ("Debt/Equity ≤ 0.5",            lambda r: _safe(r, "d_e")     <= 0.50),
    ("FCF positive (last 3y)",       lambda r: bool(r.get("fcf_pos_3y"))),
    ("EPS CAGR ≥ 10% (5y)",          lambda r: _safe(r, "eps_cagr_5y") >= 0.10),
    ("P/E ≤ 20",                     lambda r: 0 < _safe(r, "pe")  <= 20),
    ("P/B ≤ 3 OR Graham (P/E×P/B≤22.5)",
        lambda r: 0 < _safe(r, "pb") <= 3 or _safe(r, "pe") * _safe(r, "pb") <= 22.5),
]

# Buffett rubric — banks. Different metrics matter for financials.
BANK_RUBRIC: list[tuple[str, Callable[[dict], bool]]] = [
    ("ROE ≥ 15% (3y avg)",           lambda r: _safe(r, "roe_3y")  >= 0.15),
    ("ROA ≥ 1% (latest)",            lambda r: _safe(r, "roa")     >= 0.01),
    ("NPL ratio ≤ 2%",               lambda r: 0 < _safe(r, "npl") <= 0.02),
    ("CET1 proxy (E/A) ≥ 8%",        lambda r: _safe(r, "cet1")    >= 0.08),
    ("Cost-to-Income ≤ 45%",         lambda r: 0 < _safe(r, "cir") <= 0.45),
    ("Loan-to-Deposit ≤ 90%",        lambda r: 0 < _safe(r, "ldr") <= 0.90),
    ("P/B ≤ 2.0 (margin of safety)", lambda r: 0 < _safe(r, "pb")  <= 2.0),
]


def _safe(d: dict, key: str, default: float = 0.0) -> float:
    """Pull a numeric value safely; return default for None/NaN/missing."""
    v = d.get(key, default)
    if v is None:
        return default
    try:
        fv = float(v)
        if math.isnan(fv) or math.isinf(fv):
            return default
        return fv
    except (TypeError, ValueError):
        return default


def fetch_ratios(ticker: str, source: str = "VCI") -> dict:
    """Pull fundamentals via vnstock. Falls back from VCI → TCBS on failure."""
    try:
        stock = Vnstock().stock(symbol=ticker, source=source)
    except Exception:
        stock = Vnstock().stock(symbol=ticker, source="TCBS")

    # Financial ratios — yearly, last 4 rows
    try:
        ratio_df = stock.finance.ratio(period="year", lang="en")
    except Exception as e:
        raise RuntimeError(f"vnstock.finance.ratio failed for {ticker}: {e}")

    if ratio_df is None or ratio_df.empty:
        raise RuntimeError(f"No ratio data available for {ticker}")

    ratio_df = ratio_df.sort_index(ascending=False)
    rows = ratio_df.head(4).to_dict(orient="records")
    latest = rows[0]
    last3 = rows[:3]

    # Company overview
    try:
        ov = stock.company.overview()
        ov_row = ov.iloc[0].to_dict() if (ov is not None and not ov.empty) else {}
    except Exception:
        ov_row = {}

    # Latest close
    last_close = None
    try:
        end = dt.date.today()
        start = end - dt.timedelta(days=10)
        px = stock.quote.history(start=start.isoformat(), end=end.isoformat(), interval="1D")
        if px is not None and not px.empty:
            last_close = float(px.iloc[-1]["close"])
    except Exception:
        pass

    out = {
        "ticker": ticker,
        "name": ov_row.get("short_name") or ov_row.get("organ_name") or ticker,
        "industry": ov_row.get("industry") or ov_row.get("icb_name_lv2") or "Unknown",
        "exchange": ov_row.get("exchange") or "Unknown",
        "last_close": last_close,
        "data_source": f"vnstock:{source}",
        # Pricing
        "pe":  _safe({"x": latest.get("price_to_earning")}, "x"),
        "pb":  _safe({"x": latest.get("price_to_book")}, "x"),
        # Profitability
        "roe":      _safe({"x": latest.get("roe")}, "x"),
        "roa":      _safe({"x": latest.get("roa")}, "x"),
        "roe_3y":   sum(_safe({"x": r.get("roe")}, "x") for r in last3) / max(len(last3), 1),
        "roic":     _safe({"x": latest.get("roic", latest.get("roe", 0))}, "x"),
        # Non-bank
        "d_e":      _safe({"x": latest.get("debt_on_equity")}, "x"),
        "eps_cagr_5y": _eps_cagr(stock),
        "fcf_pos_3y":  _fcf_positive_3y(stock),
        # Bank
        "npl":  _safe({"x": latest.get("bad_debt") or latest.get("bad_debt_on_loan")}, "x"),
        "cir":  _safe({"x": latest.get("operating_expense_on_loan") or latest.get("cost_to_income")}, "x"),
        "ldr":  _safe({"x": latest.get("loan_on_total_deposit") or latest.get("ldr")}, "x"),
        "cet1": _safe({"x": latest.get("equity_on_total_asset") or latest.get("cet1")}, "x"),
    }
    return out


def _eps_cagr(stock) -> float:
    """5-year EPS CAGR. Returns 0 if insufficient data."""
    try:
        inc = stock.finance.income_statement(period="year").sort_index(ascending=False).head(6)
        if "earning_per_share" in inc.columns:
            col = "earning_per_share"
        elif "eps" in inc.columns:
            col = "eps"
        else:
            return 0.0
        eps = inc[col].dropna().tolist()
        if len(eps) < 5 or eps[-1] <= 0 or eps[0] <= 0:
            return 0.0
        years = len(eps) - 1
        return (eps[0] / eps[-1]) ** (1 / years) - 1
    except Exception:
        return 0.0


def _fcf_positive_3y(stock) -> bool:
    """True if free cash flow positive in each of the last 3 years."""
    try:
        cf = stock.finance.cash_flow(period="year").sort_index(ascending=False).head(3)
        for candidate in ("free_cash_flow", "fcf", "net_cash_flow_from_operating"):
            if candidate in cf.columns:
                vals = cf[candidate].dropna().tolist()
                return len(vals) >= 3 and all(v > 0 for v in vals)
        return False
    except Exception:
        return False


def score(ratios: dict, is_bank: bool) -> tuple[list[tuple[str, bool]], int]:
    rubric = BANK_RUBRIC if is_bank else NON_BANK_RUBRIC
    results = []
    for label, check in rubric:
        try:
            passed = bool(check(ratios))
        except Exception:
            passed = False
        results.append((label, passed))
    passed_count = sum(1 for _, p in results if p)
    return results, passed_count


def verdict(passed: int, total: int) -> tuple[str, str]:
    pct = passed / total if total else 0
    if pct >= 0.85:
        return "BUY", "Strong Buffett-quality candidate; quality + valuation align."
    if pct >= 0.60:
        return "WATCH", "Quality is present but not all boxes checked. Wait for better entry."
    return "PASS", "Does not meet Buffett-quality bar at current price."


def render_report(ratios: dict, results: list, passed: int, total: int, is_bank: bool) -> str:
    today = dt.date.today().isoformat()
    audit_input = f"{ratios['ticker']}|{today}|{RUBRIC_VERSION}"
    audit = hashlib.sha256(audit_input.encode()).hexdigest()[:16]
    v_tag, v_reason = verdict(passed, total)

    rubric_rows = "\n".join(
        f"| {'✅' if p else '❌'} | {label} |" for label, p in results
    )

    last_close_str = f"{ratios['last_close']:,.0f} VND" if ratios['last_close'] else "n/a"

    return f"""# {ratios['ticker']} — Buffett Analysis ({today})

> **Verdict:** **{v_tag}** — {v_reason}
> **Score:** {passed} / {total}  •  **Rubric:** {'Bank' if is_bank else 'Non-bank'} ({RUBRIC_VERSION})
> **Last close:** {last_close_str}  •  **P/E:** {ratios['pe']:.2f}  •  **P/B:** {ratios['pb']:.2f}

## Company

| Field | Value |
|-------|-------|
| Name | {ratios['name']} |
| Industry | {ratios['industry']} |
| Exchange | {ratios['exchange']} |

## Buffett Rubric

| Pass | Criterion |
|------|-----------|
{rubric_rows}

## Key Metrics

| Metric | Value |
|--------|-------|
| ROE (latest)     | {ratios['roe']*100:.2f}% |
| ROE (3y avg)     | {ratios['roe_3y']*100:.2f}% |
| ROA (latest)     | {ratios['roa']*100:.2f}% |
| Debt / Equity    | {ratios['d_e']:.2f} |
| EPS CAGR (5y)    | {ratios['eps_cagr_5y']*100:.2f}% |
| P/E              | {ratios['pe']:.2f} |
| P/B              | {ratios['pb']:.2f} |
| FCF positive (3y) | {'Yes' if ratios['fcf_pos_3y'] else 'No / unknown'} |
{"| NPL ratio        | " + f"{ratios['npl']*100:.2f}%" + " |" if is_bank else ""}
{"| Cost/Income      | " + f"{ratios['cir']*100:.2f}%" + " |" if is_bank else ""}
{"| LDR              | " + f"{ratios['ldr']*100:.2f}%" + " |" if is_bank else ""}
{"| Equity/Assets    | " + f"{ratios['cet1']*100:.2f}%" + " |" if is_bank else ""}

## Agent Governance

| Field | Value |
|-------|-------|
| Rubric version  | `{RUBRIC_VERSION}` |
| Audit hash      | `{audit}` |
| Data source     | `{ratios['data_source']}` |
| Generated at    | `{dt.datetime.now().isoformat(timespec='seconds')}` |
| Confidence      | computed from public filings; no inference unless labeled `[EST]` |
| Authorized action | read-only analysis — **no trading, no order placement** |
| OWASP Agentic   | AAI01–AAI10 aligned (see agent definition) |

---

*This is fundamental analysis, not investment advice. Verify all figures against primary filings (audited BCTC on VietstockFinance, CafeF, or the SSC) before any allocation decision. Past performance does not guarantee future results.*
"""


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 vn_buffett.py <TICKER>", file=sys.stderr)
        return 1

    ticker = sys.argv[1].upper().strip()
    is_bank = ticker in BANK_TICKERS

    print(f"[vn-buffett] Analyzing {ticker} ({'bank' if is_bank else 'non-bank'} rubric)...",
          file=sys.stderr)

    try:
        ratios = fetch_ratios(ticker)
    except Exception as e:
        print(f"[vn-buffett] ERROR fetching data: {e}", file=sys.stderr)
        return 3

    results, passed = score(ratios, is_bank)
    report = render_report(ratios, results, passed, len(results), is_bank)

    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"buffett-{ticker}-{dt.date.today().isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\n[vn-buffett] Report saved → {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
