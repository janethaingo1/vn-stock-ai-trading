# 🇻🇳 VN Trading Analyst

> **AI phân tích chứng khoán Việt Nam cho Claude Code.**  
> Kết hợp TradingView MCP (biểu đồ kỹ thuật) + vnstock (dữ liệu CK VN) thành bộ skills phân tích toàn diện.  
> Trả về Trade Score 0–100 và kế hoạch giao dịch cụ thể.

> ⚠️ **Công cụ nghiên cứu, không phải lời khuyên tài chính. Tự chịu trách nhiệm khi ra quyết định đầu tư.**

---

## Mục lục

1. [Cách hoạt động](#cách-hoạt-động)
2. [Yêu cầu trước khi cài](#yêu-cầu-trước-khi-cài)
3. [Cài đặt từng bước](#cài-đặt-từng-bước)
   - [Bước 1 — Python](#bước-1--python)
   - [Bước 2 — Node.js](#bước-2--nodejs)
   - [Bước 3 — Claude Desktop](#bước-3--claude-desktop)
   - [Bước 4 — TradingView Desktop](#bước-4--tradingview-desktop)
   - [Bước 5 — vnstock-agent](#bước-5--vnstock-agent-mcp)
   - [Bước 6 — tradingview-mcp](#bước-6--tradingview-mcp)
   - [Bước 7 — Cấu hình Claude Desktop](#bước-7--cấu-hình-claude-desktop)
   - [Bước 8 — Cài Skills](#bước-8--cài-skills)
   - [Bước 9 — Khởi động TradingView](#bước-9--khởi-động-tradingview-mỗi-lần-dùng)
4. [Kiểm tra hoạt động](#kiểm-tra-hoạt-động)
5. [Các lệnh](#các-lệnh)
6. [Troubleshooting](#troubleshooting)

---

## Cách hoạt động

```
Bạn gõ: /vn-analyze VCB
              │
    ┌─────────┴──────────┐
    │                    │
TradingView MCP      vnstock MCP
(chart, giá,         (BCTC, P/E,
 RSI, volume)         ROE, tin tức)
    │                    │
    └─────────┬──────────┘
              │
       Claude tổng hợp
              │
    Trade Score 0–100
    + Kế hoạch giao dịch
```

**Hai nguồn dữ liệu:**
- **TradingView MCP**: Biểu đồ, giá realtime, indicator kỹ thuật, alert, screenshot chart
- **vnstock MCP**: Báo cáo tài chính, P/E, ROE, tin tức, bảng giá VN30, intraday

---

## Yêu cầu trước khi cài

| Phần mềm | Mục đích | Tải về |
|----------|----------|--------|
| **Python ≥ 3.8** | Chạy vnstock-agent | [python.org](https://www.python.org/downloads/) |
| **Node.js ≥ 18** | Chạy tradingview-mcp | [nodejs.org](https://nodejs.org/) |
| **Git** | Clone repo | [git-scm.com](https://git-scm.com/downloads) |
| **Claude Desktop** | Dùng Claude + MCP | [claude.ai/download](https://claude.ai/download) |
| **TradingView Desktop** | Hiển thị chart | [tradingview.com/desktop](https://www.tradingview.com/desktop/) |
| **Tài khoản TradingView** | Đăng nhập app (free OK) | [tradingview.com](https://www.tradingview.com/) |

---

## ⚡ Cài nhanh — 1 lệnh duy nhất (Khuyến nghị)

**Windows:**
```powershell
git clone https://github.com/andyluu98/vn-stock-ai-trading.git
cd vn-stock-ai-trading
.\scripts\quick-setup.ps1
```

**macOS/Linux:**
```bash
git clone https://github.com/andyluu98/vn-stock-ai-trading.git
cd vn-stock-ai-trading
./scripts/setup-mcps.sh
```

Script tự cài hết: vnstock-agent (từ vendor), tradingview-mcp, skills, Claude Desktop config.

Sau đó còn 2 việc **manual** (script không thể tự làm vì cần Admin):
1. Khởi động TradingView debug port: `& .\scripts\launch-tv-msix.ps1` (PowerShell **Admin**)
2. Restart Claude Desktop (tắt cả icon system tray)
3. Mở terminal trong thư mục repo → gõ `claude` → thử `/vn-market`

> **Quan trọng:** Phải `cd vn-stock-ai-trading` TRƯỚC khi gõ `claude` — `.mcp.json` ở repo root chỉ load khi Claude Code CLI khởi động trong thư mục đó.

---

## Hoặc cài đặt từng bước (nếu script lỗi)

### Bước 1 — Python

Tải và cài Python từ https://python.org/downloads  
> ⚠️ Khi cài trên Windows, tick vào **"Add Python to PATH"**

Kiểm tra:
```powershell
python --version   # phải ra Python 3.x.x
pip --version
```

---

### Bước 2 — Node.js

Tải và cài Node.js LTS từ https://nodejs.org

Kiểm tra:
```powershell
node --version   # phải ra v18+ hoặc cao hơn
```

---

### Bước 3 — Claude Desktop

Tải Claude Desktop từ https://claude.ai/download → cài và đăng nhập.

> **Quan trọng — chạy ở đâu:**  
> • **Claude Code CLI** (gõ `claude` trong terminal, mở repo này): Slash commands + MCP đều hoạt động (auto-load từ `.mcp.json` trong repo). ← **Khuyến nghị**  
> • **Claude Desktop app**: MCP hoạt động, slash commands phụ thuộc phiên bản.  
> Cài Claude Desktop để đăng nhập tài khoản Anthropic, sau đó nên dùng `claude` trong terminal cho trải nghiệm tốt nhất.

---

### Bước 4 — TradingView Desktop

Tải TradingView Desktop từ https://www.tradingview.com/desktop  
→ Mở app → đăng nhập tài khoản TradingView (free account là đủ).

> **Lưu ý bản Windows Store (MSIX)**: Xem Bước 9 để cách khởi động đúng.

---

### Bước 5 — vnstock-agent (MCP)

Mở PowerShell hoặc Terminal, chạy:

```powershell
# Source vnstock-agent đã có sẵn trong repo (vendor/vnstock-agent)
pip install ./vendor/vnstock-agent
```

Kiểm tra:
```powershell
python -c "from vnstock_agent import server; print('vnstock-agent OK')"
# Phải in ra: vnstock-agent OK
```

**Lấy API key miễn phí (tuỳ chọn — không có vẫn dùng được ở Guest mode):**
1. Vào https://vnstocks.com/login
2. Đăng nhập bằng Google
3. Copy API key → dùng ở Bước 7

> **Hiện tại** (tháng 5/2026): vnstocks.com đang có lỗi OAuth Google. Nếu không đăng nhập được, bỏ qua API key — Guest mode vẫn hoạt động với giới hạn 20 req/phút.

---

### Bước 6 — tradingview-mcp

Mở PowerShell, chạy:

```powershell
cd $HOME
git clone https://github.com/tradesdontlie/tradingview-mcp.git
cd tradingview-mcp
npm install
```

Sau khi xong, thư mục sẽ nằm tại:
- Windows: `C:\Users\<YOUR_USERNAME>\tradingview-mcp`
- macOS/Linux: `~/tradingview-mcp`

---

### Bước 7 — Cấu hình MCP

**Cách A — Claude Code CLI (khuyến nghị):**

Repo này có sẵn file `.mcp.json` → khi bạn `cd` vào repo và gõ `claude`, MCP `tradingview` + `vnstock` tự load. Không cần làm gì thêm. Nếu Claude hỏi approval cho MCP lần đầu, chọn "Approve".

**Cách B — Claude Desktop:**

**Windows:**

1. Mở File Explorer → paste vào thanh địa chỉ: `%APPDATA%\Claude` → Enter
2. Mở file `claude_desktop_config.json` bằng Notepad (tạo mới nếu chưa có)
3. Paste nội dung sau, **thay `<YOUR_USERNAME>`** bằng username Windows của bạn:

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": [
        "C:\\Users\\<YOUR_USERNAME>\\tradingview-mcp\\src\\server.js"
      ]
    },
    "vnstock": {
      "command": "python",
      "args": ["-m", "vnstock_agent.server"],
      "env": {
        "VNSTOCK_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> Nếu không có API key, xoá dòng `"VNSTOCK_API_KEY"` đi — vnstock vẫn chạy ở Guest mode.

> Nếu đã có MCP khác trong file (ví dụ obsidian), chỉ thêm 2 entry `tradingview` và `vnstock` vào `mcpServers`, không xoá phần còn lại.

**macOS:**

File config nằm tại: `~/Library/Application Support/Claude/claude_desktop_config.json`

Thay đường dẫn args thành:
```json
"args": ["/Users/<YOUR_USERNAME>/tradingview-mcp/src/server.js"]
```

---

### Bước 8 — Cài Skills

Clone repo này về máy (nếu chưa có):

```powershell
git clone https://github.com/andyluu98/vn-stock-ai-trading.git
cd vn-stock-ai-trading
```

**Copy skills vào Claude Code:**

Windows (PowerShell):
```powershell
# Tạo thư mục nếu chưa có
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills"

# Copy 5 skills
Copy-Item -Recurse -Force ".claude\skills\*" "$HOME\.claude\skills\"
```

macOS/Linux:
```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/
```

> ✅ Sau khi copy xong, **tắt hoàn toàn Claude Desktop** (kể cả icon dưới taskbar) rồi **mở lại** để skills có hiệu lực.

Kiểm tra:
```powershell
ls "$HOME\.claude\skills"
# Phải thấy: vn-analyze  vn-technical  vn-fundamental  vn-market  vn-report
```

---

### Bước 9 — Khởi động TradingView (Mỗi lần dùng)

TradingView phải chạy với debug port trước khi mở Claude Desktop.

**Windows — bản Microsoft Store (MSIX):**

Mở **PowerShell as Administrator** (chuột phải → Run as administrator):
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "C:\Users\<YOUR_USERNAME>\vn-stock-ai-trading\scripts\launch-tv-msix.ps1"
```

Đợi đến khi thấy dòng:
```
DevTools listening on ws://127.0.0.1:9222/...
```
→ TradingView đã sẵn sàng.

**Windows — bản .exe trực tiếp:**
```
C:\Users\<YOUR_USERNAME>\vn-stock-ai-trading\scripts\launch_tv_debug.bat
```

**macOS/Linux:**
```bash
~/tradingview-mcp/scripts/launch_tv_debug_mac.sh
```

> 💡 **Tip**: Tạo shortcut file `.ps1` hoặc `.bat` ra Desktop để 1 click mỗi ngày.

---

## Kiểm tra hoạt động

Sau khi hoàn thành các bước trên:

1. **Khởi động TradingView** (Bước 9)
2. **Tắt hoàn toàn Claude Desktop** (kể cả icon dưới taskbar) → mở lại
3. Trong cửa sổ chat mới, gõ từng lệnh sau để kiểm tra:

```
Kiểm tra kết nối TradingView: dùng tv_health_check
```
✅ Thành công nếu thấy `"cdp_connected": true`

```
/vn-market
```
✅ Thành công nếu Claude trả về tổng quan VN-Index, VN30

```
/vn-technical VCB
```
✅ Thành công nếu Claude chụp chart VCB và phân tích kỹ thuật

---

## Các lệnh

| Lệnh | Mô tả | Thời gian |
|------|-------|-----------|
| `/vn-analyze VCB` | 🏆 Phân tích toàn diện — Trade Score 0-100, kế hoạch giao dịch | ~2-3 phút |
| `/vn-buffett VCB` | 🎩 Phân tích Warren Buffett — 12 nguyên tắc, Moat, Owner Earnings, Margin of Safety | ~2-3 phút |
| `/vn-technical VCB` | 📈 Kỹ thuật nhanh — xu hướng, hỗ trợ/kháng cự, tín hiệu vào | ~30 giây |
| `/vn-fundamental VCB` | 📋 Cơ bản sâu — BCTC, P/E, ROE, định giá nội tại | ~1 phút |
| `/vn-market` | 🌐 Tổng quan thị trường — VN-Index, VN30, top tăng/giảm | ~30 giây |
| `/vn-report VCB` | 📄 Xuất báo cáo HTML đầy đủ mở trên trình duyệt | ~3-5 phút |

**Ví dụ mã CK có thể dùng:**
`VCB` `VNM` `FPT` `HPG` `MWG` `TCB` `BID` `CTG` `ACB` `VIC` `SSI` `VHM`

---

## Ví dụ output `/vn-analyze VCB`

```
═══════════════════════════════════════
📊 PHÂN TÍCH: VCB — Vietcombank
   Ngày: 19/05/2026  |  Giá: 64,400 đ
═══════════════════════════════════════

🏆 TRADE SCORE: 72/100 — 🟢 MUA

📈 KỸ THUẬT (26/35)
   Xu hướng: Tăng ngắn hạn sau đáy 56,500
   Hỗ trợ: 62,000 đ  |  Kháng cự: 66,700 đ
   Volume: 2.7× TB — xác nhận breakout mạnh

📋 CƠ BẢN (26/35)
   P/E: 12.3  |  P/B: 2.1  |  ROE: 18.5%
   Doanh thu YoY: +14%  |  LNST YoY: +22%

🌐 THỊ TRƯỜNG (14/20)
   VN-Index: Hồi phục từ vùng hỗ trợ 1,200
   Ngành NH: Outperform thị trường +3.2%

⚠️ RỦI RO (6/10)
   Lãi suất, nợ xấu tiềm ẩn

🎯 KẾ HOẠCH GIAO DỊCH
   Vùng mua: 62,000 – 64,000 đ
   Cắt lỗ  : 59,500 đ (-7%)
   Mục tiêu: 72,000 đ (+12%)
   Tỷ lệ R:R = 1:1.7
```

---

## Nguồn dữ liệu & Độ trễ

| Dữ liệu | Nguồn | Độ trễ |
|---------|-------|--------|
| Giá, chart HOSE/HNX | TradingView | ~15 phút (free plan) |
| Intraday, bảng giá realtime | vnstock → VCI/KBS | Vài giây |
| BCTC, P/E, ROE | vnstock → TCBS/VCI | Ngày |
| Tin tức, sự kiện | vnstock → nhiều nguồn | Vài giờ |

> Để có giá realtime không trễ cho CK VN: cần tài khoản TradingView trả phí hoặc dùng vnstock intraday trực tiếp.

---

## Troubleshooting

**❌ `tv_health_check` trả về lỗi "fetch failed"**
→ TradingView chưa chạy với debug port. Chạy lại Bước 9.
→ Kiểm tra: mở trình duyệt vào `http://localhost:9222` — nếu thấy JSON là OK.

**❌ Skills không xuất hiện trong Claude**
→ Kiểm tra đã copy vào đúng thư mục `~/.claude/skills/` chưa.
→ Tắt hoàn toàn Claude Desktop (kể cả system tray) rồi mở lại.

**❌ vnstock-mcp lỗi "command not found" / MCP không kết nối được**
→ Chạy lại từ thư mục repo: `pip install ./vendor/vnstock-agent`
→ Config hiện tại đã dùng `"command": "python", "args": ["-m", "vnstock_agent.server"]` — không phụ thuộc PATH của Scripts dir.

**❌ Cài đặt Windows: "execution policy" error**
→ Chạy lệnh này trước: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

**❌ vnstocks.com không đăng nhập được (lỗi OAuth)**
→ Bỏ qua API key, xoá dòng `VNSTOCK_API_KEY` trong config.
→ Guest mode vẫn hoạt động: 20 req/phút, 4 kỳ BCTC.

**❌ TradingView bản MSIX không tìm thấy exe**
→ Dùng `scripts/launch-tv-msix.ps1` thay vì `.bat` (yêu cầu PowerShell Admin).

---

## Cấu trúc repo

```
vn-stock-ai-trading/
├── .claude/
│   └── skills/
│       ├── vn-analyze/       # Flagship: phân tích toàn diện
│       ├── vn-buffett/       # 🎩 Warren Buffett value investing
│       ├── vn-technical/     # Kỹ thuật via TradingView
│       ├── vn-fundamental/   # Cơ bản via vnstock
│       ├── vn-market/        # Tổng quan thị trường
│       └── vn-report/        # Xuất báo cáo HTML
├── vendor/
│   └── vnstock-agent/           # Source vnstock-agent (MIT, mrgoonie) — vendored
├── config/
│   └── claude-desktop-config-template.json   # Template cấu hình MCP
├── scripts/
│   ├── setup-mcps.sh          # Cài đặt tự động (macOS/Linux)
│   ├── launch-tv-msix.ps1     # Khởi động TV bản Store (Windows Admin)
│   └── launch_tv_debug.bat    # Khởi động TV bản .exe (Windows)
└── README.md
```

---

## Credits & Third-party

| Component | Source | License |
|-----------|--------|---------|
| `vendor/vnstock-agent/` | [mrgoonie/vnstock-agent](https://github.com/mrgoonie/vnstock-agent) — vendored vào repo | MIT |
| `vnstock` (Python lib, cài qua pip) | [thinh-vu/vnstock](https://github.com/thinh-vu/vnstock) | — |
| `tradingview-mcp` (clone vào `~/tradingview-mcp`) | [tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp) | — |

---

*⚠️ Không phải lời khuyên tài chính. Chỉ dùng cho mục đích nghiên cứu và học tập.*
