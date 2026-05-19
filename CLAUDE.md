# CLAUDE.md — vn-trading-analyst

Khi user mở repo này trong Claude Code, hãy **tự động chạy setup** theo hướng dẫn bên dưới — không cần user gõ thêm lệnh nào.

---

## Mô tả repo

Bộ skills phân tích chứng khoán Việt Nam cho Claude Code:
- **TradingView MCP** — chart kỹ thuật, giá realtime, vẽ trendline, tạo alert
- **vnstock MCP** — BCTC, P/E, ROE, bảng giá VN30, tin tức
- **5 skills**: `/vn-analyze`, `/vn-technical`, `/vn-fundamental`, `/vn-market`, `/vn-report`

---

## Auto-Setup Protocol

Khi user nói "cài đặt", "setup", "giúp tôi cài", hoặc mở repo lần đầu, hãy thực hiện theo thứ tự:

### Bước 1 — Phát hiện OS

```bash
# Detect OS
uname -s 2>/dev/null || echo "Windows"
```

- **Windows**: dùng PowerShell (`PowerShell` tool)
- **macOS/Linux**: dùng Bash (`Bash` tool)

### Bước 2 — Kiểm tra prerequisites

**Windows:**
```powershell
python --version
node --version
git --version
```

**macOS/Linux:**
```bash
python3 --version && node --version && git --version
```

Nếu thiếu tool nào → báo user tải về:
- Python: https://python.org/downloads (Windows: tick "Add Python to PATH")
- Node.js: https://nodejs.org (chọn LTS)
- Git: https://git-scm.com/downloads

### Bước 3 — Cài vnstock-agent

```bash
pip install vnstock-agent
```

Kiểm tra: `vnstock-mcp --help`

### Bước 4 — Clone & cài tradingview-mcp

**Windows:**
```powershell
if (-not (Test-Path "$HOME\tradingview-mcp")) {
    git clone https://github.com/tradesdontlie/tradingview-mcp.git "$HOME\tradingview-mcp"
    cd "$HOME\tradingview-mcp" && npm install
}
```

**macOS/Linux:**
```bash
if [ ! -d ~/tradingview-mcp ]; then
    git clone https://github.com/tradesdontlie/tradingview-mcp.git ~/tradingview-mcp
    cd ~/tradingview-mcp && npm install
fi
```

### Bước 5 — Copy skills vào Claude Code

**Windows:**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills"
Copy-Item -Recurse -Force ".claude\skills\*" "$HOME\.claude\skills\"
```

**macOS/Linux:**
```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/
```

Xác nhận: `ls "$HOME\.claude\skills"` phải thấy 5 thư mục: `vn-analyze vn-technical vn-fundamental vn-market vn-report`

### Bước 6 — Cấu hình Claude Desktop

Lấy username:
- Windows: `$env:USERNAME`
- macOS/Linux: `whoami`

**Tạo/cập nhật claude_desktop_config.json:**

Windows config path: `$env:APPDATA\Claude\claude_desktop_config.json`
macOS config path: `~/Library/Application Support/Claude/claude_desktop_config.json`

Nội dung cần thêm vào `mcpServers`:

```json
"tradingview": {
  "command": "node",
  "args": ["<ĐƯỜNG_DẪN_ĐẾN_tradingview-mcp>/src/server.js"]
},
"vnstock": {
  "command": "vnstock-mcp",
  "env": {
    "VNSTOCK_API_KEY": "your_api_key_here"
  }
}
```

Thay `<ĐƯỜNG_DẪN_ĐẾN_tradingview-mcp>`:
- Windows: `C:\Users\<username>\tradingview-mcp`
- macOS: `/Users/<username>/tradingview-mcp`

> Nếu user chưa có API key → xóa dòng `VNSTOCK_API_KEY` — vnstock vẫn chạy ở Guest mode (20 req/phút).

> Nếu file config đã có nội dung khác → chỉ **thêm** 2 entry trên vào `mcpServers`, không ghi đè toàn bộ file.

### Bước 7 — Hướng dẫn khởi động TradingView

Sau khi setup xong, nhắc user:

**Windows (bản Microsoft Store):**
```
1. Mở PowerShell as Administrator
2. Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
3. & "C:\Users\<username>\vn-trading-analyst\scripts\launch-tv-msix.ps1"
4. Đợi thấy: "CDP ready at http://localhost:9222"
```

**Windows (bản .exe):**
```
Chạy: scripts\launch_tv_debug.bat
```

**macOS/Linux:**
```
~/tradingview-mcp/scripts/launch_tv_debug_mac.sh
```

### Bước 8 — Restart Claude Desktop

Nhắc user: **Tắt hoàn toàn Claude Desktop** (kể cả icon dưới system tray) rồi mở lại.

### Bước 9 — Kiểm tra

Sau khi user mở lại Claude Desktop và quay lại chat:
```
Kiểm tra kết nối: tv_health_check
```
→ Thành công nếu `"cdp_connected": true`

---

## Lệnh hay dùng

| Lệnh | Tác dụng |
|------|----------|
| `/vn-analyze VCB` | Phân tích toàn diện, Trade Score 0-100 |
| `/vn-technical VCB` | Kỹ thuật nhanh qua TradingView |
| `/vn-fundamental VCB` | Cơ bản sâu qua vnstock |
| `/vn-market` | Tổng quan VN-Index, VN30 |
| `/vn-report VCB` | Xuất báo cáo HTML |

---

## Troubleshooting nhanh

| Lỗi | Cách xử lý |
|-----|-----------|
| `tv_health_check` fail | TradingView chưa chạy với debug port — chạy lại Bước 7 |
| Skills không thấy trong Claude | Chưa restart Claude Desktop — tắt hẳn rồi mở lại |
| `vnstock-mcp: command not found` | Đổi config: `"command": "python", "args": ["-m", "vnstock_agent.mcp"]` |
| Execution policy error (Windows) | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| vnstocks.com OAuth lỗi | Xóa dòng `VNSTOCK_API_KEY` trong config — dùng Guest mode |
| Script .ps1 không tìm thấy TV | Đảm bảo TradingView cài từ Microsoft Store, chạy PowerShell as Admin |

---

## Cấu trúc repo

```
vn-trading-analyst/
├── CLAUDE.md                    ← file này
├── README.md                    ← hướng dẫn đầy đủ cho người dùng
├── .claude/skills/              ← 5 skills phân tích
│   ├── vn-analyze/
│   ├── vn-technical/
│   ├── vn-fundamental/
│   ├── vn-market/
│   └── vn-report/
├── config/
│   └── claude-desktop-config-template.json
└── scripts/
    ├── setup-mcps.ps1           ← setup tự động Windows
    ├── setup-mcps.sh            ← setup tự động macOS/Linux
    ├── launch-tv-msix.ps1       ← khởi động TV bản Store (Windows Admin)
    └── launch_tv_debug.bat      ← khởi động TV bản .exe (Windows)
```
