# quick-setup.ps1 — One-command Windows setup for vn-stock-ai-trading
# Usage: from repo root, run:  .\scripts\quick-setup.ps1
# Does EVERYTHING except launching TradingView (needs Admin separately)

$ErrorActionPreference = "Continue"
$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  vn-stock-ai-trading — Quick Setup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Prereqs
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow
$missing = @()
foreach ($cmd in @("python","node","git","pip","npm")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { $missing += $cmd }
}
if ($missing.Count -gt 0) {
    Write-Host "  ERROR: Missing tools: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "  Install:" -ForegroundColor Yellow
    Write-Host "    Python: https://python.org/downloads (tick 'Add to PATH')" -ForegroundColor Gray
    Write-Host "    Node:   https://nodejs.org (LTS)" -ForegroundColor Gray
    Write-Host "    Git:    https://git-scm.com/downloads" -ForegroundColor Gray
    exit 1
}
Write-Host "  OK: Python $(python --version 2>&1), Node $(node --version), Git $(git --version)" -ForegroundColor Green

# 2. Install vnstock-agent from vendored source
Write-Host ""
Write-Host "[2/6] Installing vnstock-agent (from vendor/)..." -ForegroundColor Yellow
$vendorPath = Join-Path $repoRoot "vendor\vnstock-agent"
pip install --user $vendorPath -q 2>&1 | Out-String -Stream | Where-Object { $_ -match "Successfully|ERROR" } | ForEach-Object { Write-Host "  $_" }
if (Get-Command vnstock-mcp -ErrorAction SilentlyContinue) {
    Write-Host "  OK: vnstock-mcp available" -ForegroundColor Green
} else {
    Write-Host "  WARN: vnstock-mcp not in PATH — add Python Scripts folder to PATH" -ForegroundColor Yellow
}

# 3. Clone & install tradingview-mcp
Write-Host ""
Write-Host "[3/6] Setting up tradingview-mcp..." -ForegroundColor Yellow
$tvDir = "$HOME\tradingview-mcp"
if (Test-Path "$tvDir\src\server.js") {
    Write-Host "  OK: Already installed at $tvDir" -ForegroundColor Green
} else {
    git clone https://github.com/tradesdontlie/tradingview-mcp.git $tvDir 2>&1 | Out-Null
    Push-Location $tvDir; npm install --silent 2>&1 | Out-Null; Pop-Location
    Write-Host "  OK: Cloned + npm install at $tvDir" -ForegroundColor Green
}

# 4. Copy skills to global ~/.claude/skills/
Write-Host ""
Write-Host "[4/6] Installing skills to ~/.claude/skills/..." -ForegroundColor Yellow
$skillsDest = "$HOME\.claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDest | Out-Null
Copy-Item -Recurse -Force "$repoRoot\.claude\skills\*" $skillsDest
$installed = Get-ChildItem $skillsDest -Directory | Where-Object { $_.Name -like "vn-*" } | Select-Object -ExpandProperty Name
Write-Host "  OK: $($installed.Count) skills installed: $($installed -join ', ')" -ForegroundColor Green

# 5. Merge Claude Desktop config
Write-Host ""
Write-Host "[5/6] Updating Claude Desktop config..." -ForegroundColor Yellow
$cfg = "$env:APPDATA\Claude\claude_desktop_config.json"
$cfgDir = Split-Path -Parent $cfg
New-Item -ItemType Directory -Force -Path $cfgDir | Out-Null
if (Test-Path $cfg) {
    Copy-Item $cfg "$cfg.bak" -Force
    $json = Get-Content $cfg -Raw | ConvertFrom-Json
} else {
    $json = [PSCustomObject]@{ mcpServers = [PSCustomObject]@{} }
}
if (-not $json.mcpServers) {
    $json | Add-Member -Name mcpServers -Value ([PSCustomObject]@{}) -MemberType NoteProperty -Force
}
$tvPath = "$HOME\tradingview-mcp\src\server.js"
$json.mcpServers | Add-Member -Name "tradingview" -Value ([PSCustomObject]@{command="node"; args=@($tvPath)}) -MemberType NoteProperty -Force
# Use 'python -m vnstock_agent.server' — works even if Python Scripts not in PATH
$json.mcpServers | Add-Member -Name "vnstock" -Value ([PSCustomObject]@{
    command="python"; args=@("-m","vnstock_agent.server")
}) -MemberType NoteProperty -Force
$json | ConvertTo-Json -Depth 10 | Set-Content $cfg -Encoding UTF8
Write-Host "  OK: Added tradingview + vnstock to $cfg" -ForegroundColor Green

# 6. Final report
Write-Host ""
Write-Host "[6/6] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  Next steps (manual)" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Launch TradingView with debug port (PowerShell as ADMIN):" -ForegroundColor White
Write-Host "   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass" -ForegroundColor DarkGray
Write-Host "   & `"$repoRoot\scripts\launch-tv-msix.ps1`"" -ForegroundColor DarkGray
Write-Host ""
Write-Host "2. Restart Claude Desktop COMPLETELY (kill from system tray)" -ForegroundColor White
Write-Host ""
Write-Host "3. Test in Claude Code CLI:" -ForegroundColor White
Write-Host "   cd `"$repoRoot`"" -ForegroundColor DarkGray
Write-Host "   claude" -ForegroundColor DarkGray
Write-Host "   > /vn-market" -ForegroundColor DarkGray
Write-Host ""
