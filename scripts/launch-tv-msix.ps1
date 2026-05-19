# Launch TradingView MSIX with CDP debug port
# Run as Administrator

param([int]$Port = 9222)

Write-Host "=== TradingView MSIX Launcher ===" -ForegroundColor Cyan

# Step 1: Auto-discover TradingView package (works across all versions)
Write-Host "[1/4] Locating TradingView package..." -ForegroundColor Yellow
$tvFolder = Get-ChildItem "C:\Program Files\WindowsApps" -Directory -Filter "TradingView.Desktop_*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending | Select-Object -First 1

if (-not $tvFolder) {
    Write-Host "ERROR: TradingView MSIX package not found in WindowsApps." -ForegroundColor Red
    Write-Host "       Make sure TradingView is installed from the Microsoft Store." -ForegroundColor Yellow
    exit 1
}

Write-Host "      Found package: $($tvFolder.Name)" -ForegroundColor Green

# Grant access if needed (requires Admin)
$tvExe = Join-Path $tvFolder.FullName "TradingView.exe"
try {
    Get-Acl $tvExe -ErrorAction Stop | Out-Null
} catch {
    Write-Host "      Access denied — taking ownership..." -ForegroundColor Yellow
    takeown /f $tvFolder.FullName /r /d y 2>$null | Out-Null
    icacls $tvFolder.FullName /grant "Administrators:(OI)(CI)F" /t /q 2>$null | Out-Null
}

# Step 2: Verify exe exists
Write-Host "[2/4] Checking exe..." -ForegroundColor Yellow
if (-not (Test-Path $tvExe)) {
    $found = Get-ChildItem $tvFolder.FullName -Filter "TradingView*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $tvExe = $found.FullName
    } else {
        Write-Host "ERROR: TradingView.exe not found inside package folder." -ForegroundColor Red
        exit 1
    }
}
Write-Host "      Found: $tvExe" -ForegroundColor Green

# Step 3: Kill existing instances
Write-Host "[3/4] Stopping existing TradingView..." -ForegroundColor Yellow
Get-Process -Name "TradingView" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "      Done" -ForegroundColor Green

# Step 4: Launch with CDP
Write-Host "[4/4] Launching with --remote-debugging-port=$Port ..." -ForegroundColor Yellow
Start-Process -FilePath $tvExe -ArgumentList "--remote-debugging-port=$Port"
Write-Host "      Launched! Waiting for CDP..." -ForegroundColor Green

# Wait for CDP to become available
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest "http://localhost:$Port/json/version" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "`nCDP ready at http://localhost:$Port" -ForegroundColor Green
        Write-Host $r.Content
        $ready = $true
        break
    } catch {
        Write-Host "  Still waiting ($($i*2+2)s)..." -ForegroundColor Gray
    }
}

if (-not $ready) {
    Write-Host "`nCDP not responding after 30s." -ForegroundColor Red
    Write-Host "Try opening http://localhost:$Port in browser to check." -ForegroundColor Yellow
}
