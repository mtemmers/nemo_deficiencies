[CmdletBinding()]
param(
  [int]$Port = 8000,
  [string]$TaskName = "NEMO Deficiencies",
  [switch]$StartNow
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$startScript = Join-Path $projectRoot "start.ps1"

if (-not (Test-Path -LiteralPath $startScript)) {
  throw "Startskript nicht gefunden: $startScript"
}

$powerShellPath = (Get-Process -Id $PID).Path
$userId = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$arguments = '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -Port {1}' -f $startScript, $Port

$action = New-ScheduledTaskAction `
  -Execute $powerShellPath `
  -Argument $arguments `
  -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$principal = New-ScheduledTaskPrincipal `
  -UserId $userId `
  -LogonType Interactive `
  -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew

Register-ScheduledTask `
  -TaskName $TaskName `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Description "Startet NEMO Deficiencies bei der Windows-Anmeldung auf Port $Port." `
  -Force | Out-Null

if ($StartNow) {
  Start-ScheduledTask -TaskName $TaskName
}

Write-Host "Autostart '$TaskName' ist fuer $userId eingerichtet."
Write-Host "Anwendung: http://127.0.0.1:$Port"
if (-not $StartNow) {
  Write-Host "Der automatische Start erfolgt bei der naechsten Windows-Anmeldung."
}
