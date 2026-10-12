# NEMO Deficiencies Server Restart Script
# Stoppt den aktuellen Server und startet ihn neu

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEMO Deficiencies Server Restart" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory of this script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if .venv exists
if (-not (Test-Path -LiteralPath ".venv")) {
    Write-Host "ERROR: Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host "Please ensure you are in the project root directory." -ForegroundColor Red
    exit 1
}

# Kill any existing Python processes on port 8000
Write-Host "Prüfe auf bestehende Prozesse auf Port 8000..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host "Beende bestehende Prozesse..." -ForegroundColor Yellow
    foreach ($process in $processes) {
        $proc = Get-Process -Id $process.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Beende Prozess: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
        }
    }
}

Write-Host "Aktiviere Virtual Environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starte Server..." -ForegroundColor Yellow
Write-Host "Server läuft auf: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Zum Beenden: Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Start the server
& ".\.venv\Scripts\python" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

Write-Host ""
Write-Host "Server beendet." -ForegroundColor Yellow
