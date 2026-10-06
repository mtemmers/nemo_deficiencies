param(
  [int]$Port = 8000
)

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listeners) {
  Write-Host "Auf Port $Port läuft keine Anwendung."
  exit 0
}

$listeners | ForEach-Object { Stop-Process -Id $_.OwningProcess }
Write-Host "NEMO Deficiencies auf Port $Port wurde beendet."
