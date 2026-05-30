# vn-buffett — Phân tích theo Phong cách Warren Buffett

Đánh giá cổ phiếu Việt Nam qua lăng kính đầu tư giá trị của Warren Buffett.
Áp dụng 12 nguyên tắc (Tenets) của Buffett, hệ thống chấm điểm Moat,
phân tích Owner Earnings, và Margin of Safety — cho kết quả
**Buffett Score 0-100** cùng khuyến nghị ĐẦU TƯ DÀI HẠN.

> ⚠️ Đây là công cụ nghiên cứu mô phỏng tư duy Buffett, không phải lời khuyên tài chính.

## Trigger

`/vn-buffett <SYMBOL>` hoặc khi user nói:
- "phân tích theo Buffett", "Warren Buffett", "value investing"
- "đầu tư giá trị", "moat", "lợi thế cạnh tranh"
- "margin of safety", "biên an toàn", "intrinsic value"
- "owner earnings", "dòng tiền chủ sở hữu"

## Input

```
/vn-buffett <SYMBOL>   # VD: /vn-buffett VCB
```

---

## Triết lý cốt lõi — The Buffett Way

> "Giá là thứ bạn trả. Giá trị là thứ bạn nhận." — Warren Buffett

Phân tích dựa trên 4 trụ cột & 12 nguyên tắc (Tenets):

| Trụ cột | Nguyên tắc | Trọng số |
|---------|-----------|----------|
| 🏢 **Doanh nghiệp** (Business Tenets) | 3 tiêu chí | 25% |
| 👔 **Ban lãnh đạo** (Management Tenets) | 3 tiêu chí | 20% |
| 💰 **Tài chính** (Financial Tenets) | 4 tiêu chí | 30% |
| 📐 **Giá trị** (Value Tenets) | 2 tiêu chí | 25% |

---

## Workflow

### Bước 1 — Thu thập dữ liệu (song song)

**Agent A — Financials (vnstock MCP):**
- `stock_overview(<SYMBOL>)` → ngành, mô tả kinh doanh, vốn hóa
- `income_statement(<SYMBOL>, period="annual")` → KQKD 5 năm (nếu có, tối thiểu 3 năm)
- `balance_sheet(<SYMBOL>, period="annual")` → BCĐKT 5 năm
- `cash_flow(<SYMBOL>, period="annual")` → LCTT 5 năm
- `financial_ratio(<SYMBOL>, period="annual")` → ROE, ROA, P/E, P/B, EPS, biên LN
- `dividend_history(<SYMBOL>)` → lịch sử cổ tức
- `company_news(<SYMBOL>)` → 10 tin tức gần nhất

**Agent B — Market Data (TradingView MCP):**
- `chart_set_symbol("HOSE:<SYMBOL>")` → đổi chart
- `chart_set_timeframe("M")` → khung THÁNG (Buffett nhìn dài hạn)
- `quote_get()` → giá hiện tại
- `data_get_ohlcv(count=120)` → 120 nến tháng (~10 năm)
- `capture_screenshot()` → chụp chart dài hạn

**Agent C — So sánh ngành (vnstock MCP):**
- `market_overview()` → bối cảnh chung
- `price_board("VN30")` → so sánh P/E, ROE ngành

---

### Bước 2 — Phân tích 12 Nguyên tắc Buffett

#### 🏢 TRỤ CỘT 1: DOANH NGHIỆP (Business Tenets) — 25%

**Tenet 1 — Doanh nghiệp đơn giản, dễ hiểu (Simple & Understandable)**
- Mô hình kinh doanh có thể giải thích trong 1 đoạn ngắn?
- Sản phẩm/dịch vụ cốt lõi là gì? Có rõ ràng không?
- Thuộc "Circle of Competence" — lĩnh vực dễ đánh giá?
- **Chấm điểm:** 0-10

**Tenet 2 — Lịch sử hoạt động ổn định (Consistent Operating History)**
- Doanh thu tăng liên tục ≥5 năm (không giảm >10% quá 1 năm)?
- LNST ổn định, không có cú sốc bất thường?
- Mô hình kinh doanh không thay đổi xoành xoạch?
- **Chấm điểm:** 0-10 (dựa trên dữ liệu KQKD 5 năm)

**Tenet 3 — Triển vọng dài hạn thuận lợi (Favorable Long-term Prospects)**
- Ngành có xu hướng tăng trưởng dài hạn?
- Sản phẩm/dịch vụ có bị disrupted bởi công nghệ?
- Nhu cầu thị trường có bền vững 10+ năm?
- **Chấm điểm:** 0-10

#### 👔 TRỤ CỘT 2: BAN LÃNH ĐẠO (Management Tenets) — 20%

**Tenet 4 — Quản lý hợp lý (Rational Management)**
- Lợi nhuận giữ lại có tạo ra ≥1 đ giá trị thị trường cho mỗi 1 đ giữ lại?
- Chính sách cổ tức hợp lý (chia khi không có cơ hội tái đầu tư tốt)?
- Mua lại cổ phiếu quỹ khi giá thấp hơn intrinsic value?
- **Chấm điểm:** 0-10

**Tenet 5 — Trung thực với cổ đông (Candor/Transparency)**
- Báo cáo thường niên có thẳng thắn về khó khăn?
- Có tiền sử gian lận, che giấu thông tin?
- Giao dịch nội bộ: ban lãnh đạo có mua/bán bất thường?
- **Chấm điểm:** 0-10 (dựa trên tin tức + báo cáo)

**Tenet 6 — Chống lại tâm lý bầy đàn (Institutional Imperative Resistance)**
- Có copy chiến lược đối thủ một cách vô lý?
- Có mở rộng quá nhanh/đa ngành thiếu logic?
- Chi phí SG&A có kiểm soát tốt?
- **Chấm điểm:** 0-10

#### 💰 TRỤ CỘT 3: TÀI CHÍNH (Financial Tenets) — 30%

**Tenet 7 — ROE cao & bền vững (Focus on ROE, not EPS)**
- ROE trung bình 5 năm ≥ 15%? → Xuất sắc
- ROE ≥ 12%? → Tốt
- ROE có ổn định (standard deviation thấp)?
- So sánh ROE vs TB ngành
- **Chấm điểm:** 0-10

**Tenet 8 — Owner Earnings cao (Dòng tiền chủ sở hữu)**
- **Công thức Buffett:**
  ```
  Owner Earnings = LNST
    + Khấu hao/Phân bổ
    − CapEx duy trì (maintenance capex, ước ~60-70% tổng CapEx)
    − Thay đổi vốn lưu động
  ```
- Owner Earnings Yield = Owner Earnings / Vốn hóa → so với lãi suất trái phiếu CP 10 năm VN (~3-4%)
- Owner Earnings / LNST ≥ 80%? (chất lượng lợi nhuận)
- **Chấm điểm:** 0-10

**Tenet 9 — Biên lợi nhuận cao (High Profit Margins)**
- Biên lợi nhuận ròng (Net Margin) vs TB ngành
- Biên lợi nhuận gộp (Gross Margin) ≥ 40%? → Dấu hiệu Moat
- Xu hướng biên LN: tăng, ổn định hay giảm?
- **Chấm điểm:** 0-10

**Tenet 10 — Quy tắc 1 đồng (One-Dollar Premise)**
- Mỗi 1 đ lợi nhuận giữ lại có tạo ra ≥1 đ giá trị thị trường?
  ```
  Hiệu quả giữ lại = (Market Cap hiện tại − Market Cap 5 năm trước)
                      / (Tổng LNST giữ lại 5 năm)
  ```
- Kết quả ≥1.0 → ban lãnh đạo tạo giá trị; <1.0 → phá hủy giá trị
- **Chấm điểm:** 0-10

#### 📐 TRỤ CỘT 4: GIÁ TRỊ (Value Tenets) — 25%

**Tenet 11 — Xác định giá trị nội tại (Intrinsic Value)**
- **Phương pháp 1 — DCF (Discounted Cash Flow):**
  ```
  Giá trị nội tại = Σ (Owner Earnings × (1 + g)^n) / (1 + r)^n
  
  g = tốc độ tăng trưởng Owner Earnings (dùng CAGR 5 năm, tối đa 15%)
  r = discount rate = lãi suất TPCP VN 10 năm + Equity Risk Premium (~5%)
  Terminal value: Gordon Growth Model với g_terminal = 3%
  Kỳ dự báo: 10 năm
  ```
- **Phương pháp 2 — Earnings Power Value (EPV):**
  ```
  EPV = Owner Earnings trung bình 5 năm / r
  ```
- **Phương pháp 3 — P/E hợp lý:**
  ```
  P/E hợp lý = Tăng trưởng EPS CAGR × 2 (PEG ≤ 1 là hấp dẫn)
  Giá hợp lý = EPS × P/E hợp lý
  ```
- Lấy **trung bình 3 phương pháp** làm Intrinsic Value
- **Chấm điểm:** 0-10 (dựa trên chất lượng và độ tin cậy ước tính)

**Tenet 12 — Mua với Margin of Safety (Biên an toàn)**
- ```
  Margin of Safety = (Intrinsic Value − Giá thị trường) / Intrinsic Value × 100%
  ```
- MoS ≥ 30%: 🟢 Hấp dẫn (Buffett thường đòi hỏi ≥25-50%)
- MoS 15-30%: 🟡 Chấp nhận được
- MoS 0-15%: 🟠 Mua ở định giá hợp lý
- MoS < 0%: 🔴 Đắt — KHÔNG MUA
- **Chấm điểm:** 0-10

---

### Bước 3 — Phân tích MOAT (Lợi thế cạnh tranh bền vững)

Buffett chỉ đầu tư vào doanh nghiệp có **Economic Moat** rộng.

Đánh giá 5 nguồn Moat:

| Loại Moat | Dấu hiệu nhận biết | Áp dụng CK VN |
|-----------|--------------------|-----------------------|
| **Brand Power** | Người tiêu dùng chọn vì thương hiệu, sẵn sàng trả premium | VNM, SAB, MWG |
| **Switching Cost** | Khách hàng khó/tốn kém khi chuyển đổi | VCB (banking), FPT (ERP) |
| **Network Effect** | Giá trị tăng khi nhiều người dùng hơn | FPT Telecom, VNPay |
| **Cost Advantage** | Chi phí thấp hơn đối thủ → biên LN cao | HPG (thép tự chủ) |
| **Regulatory/License** | Giấy phép, rào cản pháp lý tạo độc quyền | Ngân hàng, Bảo hiểm, Viễn thông |

**Moat Rating:**
- 🏰🏰🏰 **Wide Moat** — Lợi thế bền vững ≥10 năm (Gross Margin >40%, ROE >15% ổn định)
- 🏰🏰 **Narrow Moat** — Lợi thế trung bình 5-10 năm
- 🏰 **No Moat** — Không có lợi thế rõ ràng → Buffett sẽ KHÔNG đầu tư

---

### Bước 4 — Tính Buffett Score

**Công thức tổng hợp:**

```
Buffett Score = (Business Score × 0.25)
             + (Management Score × 0.20)
             + (Financial Score × 0.30)
             + (Value Score × 0.25)

Mỗi trụ cột: Score = Σ(điểm các Tenet) / max điểm trụ cột × 100
```

**Thang điểm Buffett:**

| Điểm | Phân loại | Khuyến nghị |
|------|-----------|-------------|
| 85-100 | 🟢 **WONDERFUL COMPANY — MUA MẠNH** | "A wonderful company at a fair price" |
| 70-84 | 🟢 **GOOD COMPANY — MUA** | Doanh nghiệp tốt, giá hợp lý |
| 55-69 | 🟡 **FAIR COMPANY — THEO DÕI** | Tạm ổn, chờ giá tốt hơn hoặc cải thiện fundamentals |
| 40-54 | 🟠 **MEDIOCRE — TRÁNH** | "A fair company at a wonderful price" — vẫn rủi ro |
| 0-39 | 🔴 **CIGAR BUTT — KHÔNG ĐẦU TƯ** | Không đủ tiêu chuẩn Buffett |

> **Quy tắc vàng Buffett:** "Rule No.1: Never lose money. Rule No.2: Never forget Rule No.1."
> → Nếu Moat Rating = "No Moat" → cap Buffett Score ở tối đa 50, bất kể điểm tài chính.

---

### Bước 5 — Output

Trình bày theo template:

```
╔══════════════════════════════════════════════════════════════╗
║  🎩 PHÂN TÍCH WARREN BUFFETT: <SYMBOL> — <Tên công ty>      ║
║     Ngày: <ngày>  |  Giá: <giá> đ  |  Vốn hóa: X,XXX tỷ    ║
╚══════════════════════════════════════════════════════════════╝

🏆 BUFFETT SCORE: XX/100 — [Phân loại]
   "[Câu nói Buffett phù hợp]"

🏰 MOAT RATING: [Wide/Narrow/No Moat] [🏰🏰🏰 / 🏰🏰 / 🏰]
   Nguồn Moat: [Brand / Switching Cost / Network / Cost / Regulatory]
   Nhận xét: [...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 DOANH NGHIỆP (XX/25)
   Đơn giản & dễ hiểu : X/10  [Nhận xét]
   Lịch sử hoạt động   : X/10  [Nhận xét]
   Triển vọng dài hạn  : X/10  [Nhận xét]

👔 BAN LÃNH ĐẠO (XX/20)
   Quản lý hợp lý      : X/10  [Nhận xét]
   Trung thực           : X/10  [Nhận xét]
   Chống bầy đàn        : X/10  [Nhận xét]

💰 TÀI CHÍNH (XX/30)
   ROE bền vững         : X/10  [ROE TB 5Y: XX%, ngành: XX%]
   Owner Earnings       : X/10  [OE Yield: X.X%, vs TPCP: X.X%]
   Biên lợi nhuận       : X/10  [Net: XX%, Gross: XX%]
   Quy tắc 1 đồng      : X/10  [Hiệu quả giữ lại: X.Xx]

📐 GIÁ TRỊ (XX/25)
   Giá trị nội tại      : X/10
     DCF          : XX,XXX đ
     EPV          : XX,XXX đ
     P/E hợp lý  : XX,XXX đ
     Trung bình  : XX,XXX đ
   Margin of Safety     : X/10  [MoS: XX%]
     → Giá hiện tại [RẺ / HỢP LÝ / ĐẮT] so với Intrinsic Value

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SO SÁNH NHANH vs TIÊU CHUẨN BUFFETT

| Tiêu chí | Cổ phiếu | Buffett yêu cầu | Đạt? |
|----------|----------|-----------------|------|
| ROE TB 5Y | XX% | ≥ 15% | ✅/❌ |
| Nợ/VCP | X.X | ≤ 0.5 | ✅/❌ |
| Gross Margin | XX% | ≥ 40% | ✅/❌ |
| Net Margin xu hướng | [Tăng/Giảm] | Ổn định/Tăng | ✅/❌ |
| FCF/LNST | XX% | ≥ 80% | ✅/❌ |
| EPS tăng liên tục | [Có/Không] | Có | ✅/❌ |
| Cổ tức | XX% | Có trả | ✅/❌ |
| Margin of Safety | XX% | ≥ 25% | ✅/❌ |
| Moat | [Wide/Narrow/No] | Wide hoặc Narrow | ✅/❌ |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 LUẬN ĐIỂM ĐẦU TƯ (theo tư duy Buffett)

🐂 Bull Case — "Why Buffett would buy":
   • [...]
   • [...]

🐻 Bear Case — "Why Buffett would pass":
   • [...]
   • [...]

📌 KẾT LUẬN:
   Buffett [SẼ / SẼ KHÔNG / CÓ THỂ] đầu tư vào <SYMBOL> vì:
   [Lý do chính, 2-3 câu]

🎯 HÀNH ĐỘNG KHUYẾN NGHỊ (nếu MUA):
   Vùng giá hấp dẫn (MoS ≥30%): ≤ XX,XXX đ
   Giá hợp lý (MoS ~15%)       : ≤ XX,XXX đ
   Tầm nhìn đầu tư             : ≥ 3-5 năm
   Position sizing              : ≤ XX% danh mục (theo mức độ tự tin)

⚠️ Đây là công cụ nghiên cứu mô phỏng tư duy Warren Buffett,
   không phải lời khuyên tài chính. Tự chịu trách nhiệm khi đầu tư.
```

---

## Buffett Quotes — Chọn câu phù hợp theo kết quả

- Score 85+: "It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price."
- Score 70-84: "The stock market is a device for transferring money from the impatient to the patient."
- Score 55-69: "Only when the tide goes out do you discover who's been swimming naked."
- Score 40-54: "Price is what you pay. Value is what you get." — và giá hiện tại chưa cho thấy value.
- Score <40: "Rule No.1: Never lose money. Rule No.2: Never forget Rule No.1."

---

## Lưu ý quan trọng

- **Dữ liệu CK Việt Nam** có thể không đủ 5 năm cho một số mã mới lên sàn → điều chỉnh phân tích tương ứng và ghi rõ giới hạn.
- **Owner Earnings** là ước tính vì BCTC VN không tách riêng maintenance vs growth CapEx → dùng tỷ lệ 60-70% tổng CapEx làm maintenance.
- **Quản lý/Ban lãnh đạo** — dựa trên thông tin công khai (tin tức, báo cáo, giao dịch nội bộ). Nếu thiếu dữ liệu → chấm trung bình 5/10 và ghi rõ.
- **Moat Analysis** là đánh giá định tính — dựa trên mô tả ngành, biên LN, và vị thế cạnh tranh.
- Nếu vnstock MCP không có → dùng dữ liệu TradingView thay thế, ghi rõ nguồn và giới hạn.
- Nếu TradingView không kết nối → phân tích fundamental only, bỏ chart dài hạn.
- Luôn ghi rõ thời điểm lấy dữ liệu và các giả định đã dùng.
- **Buffett đầu tư DÀI HẠN** → khuyến nghị tầm nhìn tối thiểu 3-5 năm, KHÔNG phải trade ngắn hạn.
