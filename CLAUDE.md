# CLAUDE.md — Auto-Setup Instructions

> **Đây là file hướng dẫn cho Claude (cả Claude Code CLI và Claude Desktop).** Khi user clone repo này và nói **"cài cho tôi"**, **"setup"**, **"install"**, hoặc đơn giản là mở repo → bạn (Claude) PHẢI tự động chạy toàn bộ quy trình cài đặt bên dưới. Không hỏi gì cả nếu không cần.

---

## Mô tả repo

Bộ skills phân tích chứng khoán Việt Nam:
- **TradingView MCP** — chart, giá realtime, indicator, vẽ trendline, alert
- **vnstock MCP** — BCTC, P/E, ROE, bảng giá VN30, tin tức
- **6 skills**: `/vn-analyze`, `/vn-technical`, `/vn-fundamental`, `/vn-market`, `/vn-report`, `/vn-buffett`

## Hoạt động ở đâu

| Platform | MCP | Skills `/vn-*` | Cách dùng |
|----------|-----|----------------|-----------|
| Claude Code CLI | ✅ `.mcp.json` tự load | ✅ Từ `~/.claude/skills/` | `cd <repo> && claude` |
| Claude Desktop | ✅ `claude_desktop_config.json` | ✅ Từ `~/.claude/skills/` (mới) | Mở app sau khi setup |

Setup này configure cho **cả hai** — user chọn dùng nào cũng được.

---

# ⚙️ AUTO-SETUP PROTOCOL

**Khi user nói "cài"/"setup"/"install"** → chạy lần lượt theo thứ tự bên dưới. KHÔNG dừng lại hỏi user trừ khi gặp lỗi không tự fix được.

## ⚡ Fast path — dùng quick-setup script (KHUYẾN NGHỊ)

Nếu user đang ở Windows, **CHỈ CẦN CHẠY 1 LỆNH**:
```powershell
.\scripts\quick-setup.ps1
```
Script này tự làm bước 2-6 bên dưới (prereq check, vnstock-agent, tradingview-mcp, copy skills, update Claude Desktop config). Sau khi xong, nhảy thẳng đến Bước 7 (launch TradingView) + Bước 8 (restart Claude).

macOS/Linux:
```bash
./scripts/setup-mcps.sh
```

⚠️ **Quan trọng về session Claude Code CLI:**
- Nếu user clone repo LẦN ĐẦU rồi gõ `claude` → `.mcp.json` tự load → `/vn-market` chạy NGAY sau khi setup xong.
- Nếu user `git pull` repo về (lúc đã có session đang chạy) → MCP CHƯA load trong session hiện tại → user PHẢI exit (`/exit`) rồi gõ `claude` lại từ thư mục repo. Báo user rõ điều này.

## Manual path (nếu script lỗi)

## Bước 1 — Detect OS

```
Windows  → dùng tool `PowerShell`
macOS    → dùng tool `Bash`, command `python3` thay `python`
Linux    → dùng tool `Bash`
```

## Bước 2 — Verify prerequisites

Chạy 1 lệnh kiểm tra Python + Node + Git:

**Windows:**
```powershell
python --version; node --version; git --version
```

**macOS/Linux:**
```bash
python3 --version && node --version && git --version
```

Nếu thiếu → DỪNG và báo user link tải. KHÔNG tự cài Python/Node/Git.
- Python ≥3.8: https://python.org/downloads (Windows: **tick "Add Python to PATH"**)
- Node ≥18 LTS: https://nodejs.org
- Git: https://git-scm.com/downloads

## Bước 3 — Install vnstock-agent

**Lệnh ĐÚNG (source đã vendor sẵn trong repo, không cần clone từ GitHub):**

```bash
pip install --user ./vendor/vnstock-agent
```

> Source nằm tại `vendor/vnstock-agent/` (MIT license, attribution: mrgoonie). pip sẽ tự cài các dependency (`vnstock`, `fastmcp`, `click`, `pandas`...) từ PyPI.

Verify: `vnstock-mcp --help` phải hiện help text.

Nếu `vnstock-mcp` không có trong PATH sau khi cài → user cần thêm `~/.local/bin` (Linux/Mac) hoặc `%APPDATA%\Python\Python3xx\Scripts` (Windows) vào PATH. Báo user và tiếp tục.

## Bước 4 — Setup tradingview-mcp

**Windows:**
```powershell
if (-not (Test-Path "$HOME\tradingview-mcp\src\server.js")) {
    git clone https://github.com/tradesdontlie/tradingview-mcp.git "$HOME\tradingview-mcp"
    Push-Location "$HOME\tradingview-mcp"; npm install; Pop-Location
}
```

**macOS/Linux:**
```bash
if [ ! -f ~/tradingview-mcp/src/server.js ]; then
    git clone https://github.com/tradesdontlie/tradingview-mcp.git ~/tradingview-mcp
    (cd ~/tradingview-mcp && npm install)
fi
```

Verify: file `~/tradingview-mcp/src/server.js` tồn tại.

## Bước 5 — Copy skills vào `~/.claude/skills/`

Skills phải nằm ở **global path** để cả Claude Code CLI và Claude Desktop đều thấy.

**Windows:**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "<REPO_ROOT>\.claude\skills\*" "$HOME\.claude\skills\"
```

Trong đó `<REPO_ROOT>` là thư mục repo (lấy bằng `git rev-parse --show-toplevel` hoặc dùng `$PWD` nếu user đang cd trong repo).

**macOS/Linux:**
```bash
mkdir -p ~/.claude/skills
cp -r "$REPO_ROOT/.claude/skills/"* ~/.claude/skills/
```

Verify: `ls ~/.claude/skills/` phải thấy 6 thư mục `vn-analyze vn-technical vn-fundamental vn-market vn-report vn-buffett`.

## Bước 6 — Cấu hình Claude Desktop config

> Repo đã có `.mcp.json` cho Claude Code CLI tự load. Bước này thêm config cho **Claude Desktop**.

Path:
- Windows: `$env:APPDATA\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Logic xử lý:**
1. Nếu file CHƯA tồn tại → tạo mới với content bên dưới.
2. Nếu file ĐÃ tồn tại → đọc JSON, MERGE 2 entry `tradingview` + `vnstock` vào `mcpServers` (KHÔNG ghi đè entries cũ). Backup file gốc thành `.bak` trước khi sửa.

**Entries cần thêm (lấy username từ `$env:USERNAME` Windows / `whoami` Mac):**

```json
"tradingview": {
  "command": "node",
  "args": ["<HOME>/tradingview-mcp/src/server.js"]
},
"vnstock": {
  "command": "vnstock-mcp"
}
```

Với `<HOME>`:
- Windows: `C:\\Users\\<username>` (escape backslash)
- macOS: `/Users/<username>`

**PowerShell mẫu (Windows):**
```powershell
$cfg = "$env:APPDATA\Claude\claude_desktop_config.json"
if (Test-Path $cfg) { Copy-Item $cfg "$cfg.bak" -Force }
$json = if (Test-Path $cfg) { Get-Content $cfg -Raw | ConvertFrom-Json } else { [PSCustomObject]@{ mcpServers = [PSCustomObject]@{} } }
if (-not $json.mcpServers) { $json | Add-Member -Name mcpServers -Value ([PSCustomObject]@{}) -MemberType NoteProperty }
$tvPath = "$HOME\tradingview-mcp\src\server.js"
$json.mcpServers | Add-Member -Name "tradingview" -Value ([PSCustomObject]@{command="node"; args=@($tvPath)}) -MemberType NoteProperty -Force
$json.mcpServers | Add-Member -Name "vnstock" -Value ([PSCustomObject]@{command="vnstock-mcp"}) -MemberType NoteProperty -Force
$json | ConvertTo-Json -Depth 10 | Set-Content $cfg -Encoding UTF8
```

## Bước 7 — Hướng dẫn user khởi động TradingView (KHÔNG tự chạy)

Đây là bước user PHẢI tự làm vì cần PowerShell Admin và app GUI. Báo user theo OS:

**Windows (Microsoft Store):**
```powershell
# Mở PowerShell as ADMINISTRATOR (chuột phải → Run as Administrator)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "<REPO_ROOT>\scripts\launch-tv-msix.ps1"
# Đợi đến khi thấy: "CDP ready at http://localhost:9222"
```

**Windows (TradingView .exe thường):**
```
<REPO_ROOT>\scripts\launch_tv_debug.bat
```

**macOS:**
```bash
open -a "TradingView" --args --remote-debugging-port=9222
```

## Bước 8 — Báo user "restart Claude" + cách test

Sau khi cài xong, báo user:

1. **Restart Claude** (tắt hoàn toàn rồi mở lại):
   - Claude Desktop: tắt cả icon dưới system tray
   - Claude Code CLI: thoát terminal, mở lại
2. **Test commands:**
   - Trong Claude Code CLI (sau khi `cd <repo> && claude`): `/vn-market`
   - Trong Claude Desktop: gõ "kiểm tra kết nối tradingview" hoặc `tv_health_check`
3. Nếu thấy `"cdp_connected": true` → mọi thứ hoạt động.

---

## ✅ Verification Checklist (chạy cuối cùng để báo cáo)

Sau khi xong setup, tự verify và báo user dạng bảng:

| Mục | Cách check | Kết quả mong đợi |
|-----|-----------|------------------|
| Python | `python --version` | 3.8+ |
| Node | `node --version` | v18+ |
| vnstock-mcp | `vnstock-mcp --help` | help text |
| tradingview-mcp | `Test-Path "$HOME\tradingview-mcp\src\server.js"` | True |
| Skills | `ls ~/.claude/skills/vn-*` | 6 thư mục |
| `.mcp.json` repo | `Test-Path "<REPO>\.mcp.json"` | True |
| Claude Desktop config | có entry `tradingview` + `vnstock` | OK |

---

## Troubleshooting

| Lỗi | Fix |
|-----|-----|
| `vnstock-agent: not found on PyPI` | Dùng `pip install ./vendor/vnstock-agent` (source nằm sẵn trong repo) |
| `vnstock-mcp: command not found` sau khi pip install | Thêm Scripts folder vào PATH, hoặc đổi config thành `"command":"python","args":["-m","vnstock_agent.mcp"]` |
| `tv_health_check` fail / fetch failed | TradingView chưa chạy với debug port — chạy lại Bước 7 |
| Skills không xuất hiện | Restart Claude hoàn toàn (cả tray icon) |
| MCP không load trong Claude Code CLI | `cd` vào đúng thư mục repo trước khi gõ `claude` |
| Execution policy error | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` trước khi chạy script |
| MSIX TradingView không tìm thấy | Chạy `launch-tv-msix.ps1` từ PowerShell **Admin** |
| `pip install` denied bởi sandbox | Báo user chạy thủ công: `pip install --user ./vendor/vnstock-agent` (chạy từ thư mục repo) |

---

## Cấu trúc repo

```
vn-stock-ai-trading/
├── CLAUDE.md                    ← bạn đang đọc — auto-install instructions
├── README.md                    ← hướng dẫn cho human
├── .mcp.json                    ← MCP config cho Claude Code CLI (auto-loaded)
├── .claude/skills/              ← 6 skills /vn-*
│   ├── vn-analyze/
│   ├── vn-technical/
│   ├── vn-fundamental/
│   ├── vn-market/
│   ├── vn-report/
│   └── vn-buffett/              ← Warren Buffett value investing
├── vendor/
│   └── vnstock-agent/           ← source vendored từ mrgoonie/vnstock-agent (MIT)
├── config/
│   └── claude-desktop-config-template.json
└── scripts/
    ├── quick-setup.ps1          ← ⚡ ONE-COMMAND Windows installer (recommended)
    ├── setup-mcps.ps1           ← Windows installer (legacy)
    ├── setup-mcps.sh            ← macOS/Linux installer
    ├── launch-tv-msix.ps1       ← TradingView Store launcher (Admin)
    └── launch_tv_debug.bat      ← TradingView .exe launcher
```
