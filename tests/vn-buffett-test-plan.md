# 🧪 Test Plan: /vn-buffett Skill

> Run from: `cd ~/Desktop/Antigravity/vn-stock-ai-trading && claude`
> Prerequisites: TradingView Desktop running with debug port, vnstock MCP active

---

## How to run

1. Start TradingView: `open -a "TradingView" --args --remote-debugging-port=9222`
2. Open Claude Code: `cd ~/Desktop/Antigravity/vn-stock-ai-trading && claude`
3. Run each test below and record result

---

## ✅ Test 1 — VCB (Blue-chip bank, Wide Moat)

**Command:** `/vn-buffett VCB`

**Pass criteria:**
- [ ] Buffett Score displayed (0-100)
- [ ] Score in range 70-85+ (strong bank, high ROE)
- [ ] Moat Rating = Wide Moat (🏰🏰🏰)
- [ ] Moat sources mention: Regulatory + Switching Cost
- [ ] All 4 pillars scored: Business, Management, Financial, Value
- [ ] All 12 Tenets have individual scores (X/10)
- [ ] ROE TB 5Y shown and ≥ 15%
- [ ] Owner Earnings calculated (LNST + Khấu hao − CapEx − ∆WC)
- [ ] Intrinsic Value shown (3 methods: DCF, EPV, P/E)
- [ ] Margin of Safety % shown
- [ ] Comparison table vs Buffett standards with ✅/❌
- [ ] Bull/Bear case present
- [ ] Tầm nhìn đầu tư ≥ 3-5 năm
- [ ] Disclaimer present
- [ ] Buffett quote matches score range

**Notes:**
```




```

---

## ✅ Test 2 — VNM (Classic Buffett — Consumer Staple)

**Command:** `/vn-buffett VNM`

**Pass criteria:**
- [ ] Score likely 75-90 (dominant brand, high margins)
- [ ] Moat = Wide Moat — Brand Power
- [ ] Gross Margin ≥ 40% flagged as Moat signal
- [ ] Consistent dividend history shown
- [ ] Tenet 1 (Simple & Understandable) scores high (dairy = simple)
- [ ] Tenet 2 (Consistent History) scores high (stable revenue)
- [ ] FCF/LNST ratio shown

**Notes:**
```




```

---

## ✅ Test 3 — FPT (Tech, Consistent Growth)

**Command:** `/vn-buffett FPT`

**Pass criteria:**
- [ ] Score in range 65-80
- [ ] Moat = Narrow or Wide (Switching Cost + Brand)
- [ ] Strong EPS CAGR shown
- [ ] Tenet 3 (Long-term Prospects) scores high (digital transformation)
- [ ] P/E comparison vs industry average

**Notes:**
```




```

---

## ✅ Test 4 — HPG (Cyclical Steel)

**Command:** `/vn-buffett HPG`

**Pass criteria:**
- [ ] Score LOWER than VCB/VNM (50-65 range)
- [ ] Moat = Narrow (Cost Advantage)
- [ ] Tenet 2 (Consistent History) scores LOW due to cyclical earnings
- [ ] Volatile ROE acknowledged
- [ ] Bear case mentions commodity cycle risk

**Notes:**
```




```

---

## ✅ Test 5 — SAB (Beer Monopoly, Ultra-high Margins)

**Command:** `/vn-buffett SAB`

**Pass criteria:**
- [ ] Score 75-90 (monopoly + brand)
- [ ] Moat = Wide (Brand + Regulatory)
- [ ] Gross Margin significantly > 40%
- [ ] Tenet 1 scores high (beer = simple business)
- [ ] Dividend history present

**Notes:**
```




```

---

## ⚠️ Test 6 — HAG (Troubled Company, Negative Earnings)

**Command:** `/vn-buffett HAG`

**Pass criteria:**
- [ ] Score very low (< 40) — "CIGAR BUTT"
- [ ] Handles negative ROE correctly (not crash)
- [ ] High Nợ/VCP flagged (≥ 0.5 → ❌)
- [ ] Owner Earnings likely negative — handled gracefully
- [ ] Margin of Safety < 0% or N/A due to negative earnings
- [ ] Conclusion: "Buffett SẼ KHÔNG đầu tư"
- [ ] Bear case dominant

**Notes:**
```




```

---

## ⚠️ Test 7 — VIC (Conglomerate, High Debt)

**Command:** `/vn-buffett VIC`

**Pass criteria:**
- [ ] Tenet 1 (Simple) scores LOW (complex conglomerate)
- [ ] High Nợ/VCP flagged
- [ ] Negative FCF acknowledged
- [ ] Moat ≤ Narrow
- [ ] Score likely 40-55

**Notes:**
```




```

---

## ⚠️ Test 8 — SSI (Brokerage, Cyclical)

**Command:** `/vn-buffett SSI`

**Pass criteria:**
- [ ] Volatile ROE handling (swings with market)
- [ ] Tenet 2 (Consistent History) penalized
- [ ] Business tied to market cycle acknowledged

**Notes:**
```




```

---

## 🔴 Test 9 — Non-existent Ticker

**Command:** `/vn-buffett ABCXYZ`

**Pass criteria:**
- [ ] Does NOT crash
- [ ] Returns clear error: ticker not found or invalid
- [ ] Suggests correct format

**Notes:**
```




```

---

## 🔴 Test 10 — No Symbol Provided

**Command:** `/vn-buffett`

**Pass criteria:**
- [ ] Prompts user for a symbol
- [ ] Shows usage example: `/vn-buffett VCB`

**Notes:**
```




```

---

## 🔴 Test 11 — US Stock (Out of Scope)

**Command:** `/vn-buffett AAPL`

**Pass criteria:**
- [ ] Rejects or warns: not a Vietnamese stock
- [ ] OR: attempts analysis via TradingView with clear note about data source limitations

**Notes:**
```




```

---

## 🔴 Test 12 — Index (Not a Stock)

**Command:** `/vn-buffett VNINDEX`

**Pass criteria:**
- [ ] Rejects: this is an index, not a stock
- [ ] Does not attempt Buffett analysis on an index

**Notes:**
```




```

---

## 🔌 Test 13 — No TradingView (MCP Partial Failure)

**Setup:** Kill TradingView before running
**Command:** `/vn-buffett ACB`

**Pass criteria:**
- [ ] Falls back to fundamental-only analysis
- [ ] Clearly notes: "TradingView không kết nối, phân tích fundamental only"
- [ ] Chart screenshot section skipped gracefully
- [ ] All financial tenets still scored
- [ ] Intrinsic value still calculated

**Notes:**
```




```

---

## 🔌 Test 14 — New Listing (Limited Data)

**Command:** `/vn-buffett LPB` (or any stock with < 3 years on exchange)

**Pass criteria:**
- [ ] Notes insufficient data for 5Y metrics
- [ ] Adjusts analysis window to available data
- [ ] Lowers confidence / adds caveat
- [ ] Does not crash on missing historical periods

**Notes:**
```




```

---

## 🔄 Test 15 — Comparative: Buffett vs Trade Score

**Commands:**
1. `/vn-buffett VCB`
2. `/vn-analyze VCB`

**Pass criteria:**
- [ ] Buffett Score ≠ Trade Score (different methodologies)
- [ ] Buffett focuses on long-term (3-5Y horizon)
- [ ] Trade Score focuses on short-term signals
- [ ] Both analyze same stock but reach different emphasis
- [ ] Buffett skill does NOT include short-term technical signals (RSI, MACD)

**Notes:**
```




```

---

## 🔄 Test 16 — Comparative: Staple vs Cyclical

**Commands:**
1. `/vn-buffett VNM`
2. `/vn-buffett HPG`

**Pass criteria:**
- [ ] VNM scores higher on Tenet 2 (Consistency)
- [ ] VNM scores higher on Tenet 9 (Margins)
- [ ] HPG scores higher on Tenet 3 if steel demand outlook is positive
- [ ] Moat types are different (Brand vs Cost)
- [ ] Overall: VNM Buffett Score > HPG Buffett Score

**Notes:**
```




```

---

## 📊 Results Summary

| # | Test | Command | Score | Pass/Fail | Issues |
|---|------|---------|-------|-----------|--------|
| 1 | Blue-chip bank | `/vn-buffett VCB` | | | |
| 2 | Consumer staple | `/vn-buffett VNM` | | | |
| 3 | Tech leader | `/vn-buffett FPT` | | | |
| 4 | Cyclical steel | `/vn-buffett HPG` | | | |
| 5 | Beer monopoly | `/vn-buffett SAB` | | | |
| 6 | Troubled co. | `/vn-buffett HAG` | | | |
| 7 | Conglomerate | `/vn-buffett VIC` | | | |
| 8 | Brokerage | `/vn-buffett SSI` | | | |
| 9 | Bad ticker | `/vn-buffett ABCXYZ` | N/A | | |
| 10 | No symbol | `/vn-buffett` | N/A | | |
| 11 | US stock | `/vn-buffett AAPL` | N/A | | |
| 12 | Index | `/vn-buffett VNINDEX` | N/A | | |
| 13 | No TradingView | `/vn-buffett ACB` | | | |
| 14 | New listing | `/vn-buffett LPB` | | | |
| 15 | vs Trade Score | VCB both skills | | | |
| 16 | Staple vs Cycl. | VNM vs HPG | | | |

**Total: ___ / 16 passed**
**Date tested:**
**Tester:**
