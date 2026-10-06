param(
  [int]$Port = 8000
)

$projectRoot = $PSScriptRoot
$pythonCandidates = @(
  (Join-Path $projectRoot ".venv\Scripts\python.exe"),
  $(if ($env:CONDA_PREFIX) { Join-Path $env:CONDA_PREFIX "python.exe" }),
  (Join-Path $HOME ".conda\envs\nemo_import_export\python.exe"),
  $((Get-Command python -ErrorAction SilentlyContinue).Source)
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique

$python = $null
foreach ($candidate in $pythonCandidates) {
  & $candidate -c "import fastapi, uvicorn, nemo_library" 2>$null
  if ($LASTEXITCODE -eq 0) {
    $python = $candidate
    break
  }
}

if (-not $python) {
  throw "Keine passende Python-Umgebung gefunden. Bitte zuerst '.\.venv\Scripts\Activate.ps1' und 'python -m pip install -e .' ausführen."
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
  Write-Host "NEMO Deficiencies läuft bereits unter http://127.0.0.1:$Port"
  exit 0
}

$logDir = Join-Path $projectRoot "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$stdoutLog = Join-Path $logDir "server-output.log"
$stderrLog = Join-Path $logDir "server-error.log"

$process = Start-Process `
  -FilePath $python `
  -ArgumentList @("-m", "backend.cli", "--port", "$Port") `
  -WorkingDirectory $projectRoot `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog `
  -PassThru `
  -WindowStyle Hidden

$started = $null
for ($attempt = 0; $attempt -lt 30; $attempt++) {
  if ($process.HasExited) {
    break
  }
  $started = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  if ($started) {
    break
  }
  Start-Sleep -Milliseconds 500
}
if (-not $started) {
  $details = if (Test-Path -LiteralPath $stderrLog) { (Get-Content -LiteralPath $stderrLog -Tail 10) -join [Environment]::NewLine } else { "Kein Fehlerlog vorhanden." }
  throw "NEMO Deficiencies konnte nicht gestartet werden (Prozess $($process.Id)).`n$details"
}

Write-Host "NEMO Deficiencies läuft unter http://127.0.0.1:$Port"
Write-Host "Python: $python"
