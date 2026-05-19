# setup-mcps.ps1 — vn-trading-analyst setup for Windows
# Run in PowerShell (no Admin required)

$ErrorActionPreference = "Stop"

Write-Host "=== vn-trading-analyst Setup (Windows) ===" -ForegroundColor Cyan
Write-Host ""

# 1. Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $v = python --version 2>&1
    Write-Host "      OK: $v" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Download from https://python.org/downloads" -ForegroundColor Red
    Write-Host "       Make sure to check 'Add Python to PATH' during install." -ForegroundColor Yellow
    exit 1
}

# 2. Node.js
Write-Host "[2/5] Checking Node.js..." -ForegroundColor Yellow
try {
    $v = node --version 2>&1
    Write-Host "      OK: $v" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found. Download LTS from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# 3. Install vnstock-agent
Write-Host "[3/5] Installing vnstock-agent..." -ForegroundColor Yellow
pip install vnstock-agent -q
Write-Host "      OK: vnstock-agent installed" -ForegroundColor Green
Write-Host "      -> Get free API key at: https://vnstocks.com/login (optional)" -ForegroundColor Gray

# 4. Clone tradingview-mcp
Write-Host "[4/5] Setting up tradingview-mcp..." -ForegroundColor Yellow
$tvDir = "$HOME\tradingview-mcp"
if (Test-Path $tvDir) {
    Write-Host "      Already exists at $tvDir — skipping clone" -ForegroundColor Gray
} else {
    git clone https://github.com/tradesdontlie/tradingview-mcp.git $tvDir
    Push-Location $tvDir
    npm install
    Pop-Location
    Write-Host "      OK: cloned to $tvDir" -ForegroundColor Green
}

# 5. Copy skills
Write-Host "[5/5] Installing skills..." -ForegroundColor Yellow
$skillsDest = "$HOME\.claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDest | Out-Null
$skillsSrc = Join-Path $PSScriptRoot "..\\.claude\\skills"
$skillsSrc = (Resolve-Path $skillsSrc -ErrorAction SilentlyContinue)?.Path
if ($skillsSrc -and (Test-Path $skillsSrc)) {
    Copy-Item -Recurse -Force "$skillsSrc\*" $skillsDest
    Write-Host "      OK: skills copied to $skillsDest" -ForegroundColor Green
} else {
    Write-Host "      WARN: skills folder not found — run this script from repo root" -ForegroundColor Yellow
}

# Done
Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""

# Detect username
$username = $env:USERNAME

Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Copy config to Claude Desktop:" -ForegroundColor Gray
Write-Host "     Copy-Item '.\config\claude-desktop-config-template.json' `$env:APPDATA\Claude\claude_desktop_config.json" -ForegroundColor DarkGray
Write-Host "  2. Open the config file and replace <YOUR_USERNAME> with: $username" -ForegroundColor Gray
Write-Host "  3. (Optional) Add vnstock API key in the config" -ForegroundColor Gray
Write-Host "  4. Launch TradingView (run as Admin):" -ForegroundColor Gray
Write-Host "     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass" -ForegroundColor DarkGray
Write-Host "     & '$HOME\vn-trading-analyst\scripts\launch-tv-msix.ps1'" -ForegroundColor DarkGray
Write-Host "  5. Restart Claude Desktop completely (including system tray)" -ForegroundColor Gray
Write-Host "  6. Try: /vn-market" -ForegroundColor Green
Write-Host ""
