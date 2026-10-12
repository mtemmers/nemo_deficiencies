# Kill processes on port 8000

Write-Host "Beende alle Prozesse auf Port 8000..." -ForegroundColor Yellow

$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($processes) {
    foreach ($process in $processes) {
        $proc = Get-Process -Id $process.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Beende: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "Prozesse beendet." -ForegroundColor Green
    Start-Sleep -Seconds 1
    Write-Host "Port 8000 ist jetzt frei." -ForegroundColor Green
} else {
    Write-Host "Keine Prozesse auf Port 8000 gefunden." -ForegroundColor Green
}
