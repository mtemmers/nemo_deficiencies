[CmdletBinding()]
param(
  [string]$TaskName = "NEMO Deficiencies",
  [int]$Port = 8000,
  [switch]$StopApplication
)

$ErrorActionPreference = "Stop"
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($task) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "Autostart '$TaskName' wurde entfernt."
} else {
  Write-Host "Autostart '$TaskName' ist nicht eingerichtet."
}

if ($StopApplication) {
  & (Join-Path $PSScriptRoot "stop.ps1") -Port $Port
}
