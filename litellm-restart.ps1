# LiteLLM Server Restart Script
# Startet LiteLLM auf Port 4000

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LiteLLM Server Restart" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes on port 4000
Write-Host "Prüfe auf bestehende Prozesse auf Port 4000..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 4000 -ErrorAction SilentlyContinue
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

Write-Host ""
Write-Host "Starte LiteLLM Server..." -ForegroundColor Yellow
Write-Host "LiteLLM läuft auf: http://localhost:4000" -ForegroundColor Green
Write-Host "LiteLLM Docs: http://localhost:4000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Zum Beenden: Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Check if litellm_config.yaml exists
if (Test-Path -LiteralPath "litellm_config.yaml") {
    Write-Host "Nutze litellm_config.yaml..." -ForegroundColor Yellow
    & python -m litellm --config ./litellm_config.yaml --port 4000
} else {
    Write-Host "Starte LiteLLM ohne Konfigurationsdatei..." -ForegroundColor Yellow
    Write-Host "(Erstelle eine litellm_config.yaml für benutzerdefinierte Modelle)" -ForegroundColor Gray
    & python -m litellm --port 4000
}

Write-Host ""
Write-Host "LiteLLM beendet." -ForegroundColor Yellow
