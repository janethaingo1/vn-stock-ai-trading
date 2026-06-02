---
description: Run Buffett-style fundamental analysis on a Vietnamese stock ticker
argument-hint: <TICKER> (e.g. VCB, FPT, HPG, VHM, MWG)
allowed-tools: Bash, Read, Write
---

Run a Buffett-style fundamental analysis on the Vietnamese stock ticker: **$ARGUMENTS**

## Steps

1. Verify `vnstock` is installed:

   ```bash
   python3 -c "import vnstock; print('vnstock', vnstock.__version__)" 2>&1 || pip install -U vnstock pandas
   ```

2. Run the analyzer:

   ```bash
   python3 scripts/vn_buffett.py $ARGUMENTS
   ```

3. Output report is saved to `out/buffett-$ARGUMENTS-<YYYY-MM-DD>.md`. Read it, then present to the user:
   - **Verdict** (BUY / WATCH / PASS)
   - **Rubric score** (X of Y criteria passed)
   - **Top 3 reasons** supporting the verdict
   - **Target entry zone** if BUY or WATCH

4. If the Obsidian MCP is connected in this Claude Code session, also append the full report to `02-Areas/Investments/$ARGUMENTS Buffett Analysis.md`. If not connected, tell the user the local `out/` path so they can drag-drop into Obsidian themselves.

5. If `vn_buffett.py` errors or returns NaN for key metrics — surface the error verbatim. **Do not fabricate values.** Per Jane's integrity defaults: flag uncertainty, never invent.

## Failure modes to watch

- `vnstock` source `VCI` rate-limits at ~30 req/min. If you hit 429, retry with `source="TCBS"`.
- For unlisted or delisted tickers, vnstock returns empty DataFrames — script handles this, but verify the ticker is on HOSE/HNX/UPCOM first.
- For banks, P/B above 2.0 fails the rubric — that's intentional, not a bug. Buffett wants margin of safety on financials.
