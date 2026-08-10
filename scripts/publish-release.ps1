[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [ValidatePattern('^v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$')]
  [string]$Version,
  [switch]$BuildLocal,
  [switch]$Yes
)

$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$Version = $Version.TrimStart("v")
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
  throw "Ungültige Version '$Version'. Erwartet wird beispielsweise 1.4.0."
}
$tag = "v$Version"
$versionFile = Join-Path $projectRoot "backend\__init__.py"

Push-Location $projectRoot
try {
  git rev-parse --is-inside-work-tree | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Kein Git-Repository gefunden." }
  git remote get-url origin | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Git-Remote 'origin' fehlt." }
  git rev-parse --verify --quiet "refs/tags/$tag" | Out-Null
  if ($LASTEXITCODE -eq 0) { throw "Tag $tag existiert bereits." }

  $versionContent = [System.IO.File]::ReadAllText($versionFile)
  $updatedContent = [regex]::Replace(
    $versionContent,
    '__version__\s*=\s*"[^"]+"',
    "__version__ = `"$Version`"",
    1
  )
  if ($updatedContent -eq $versionContent -and $versionContent -notmatch [regex]::Escape("__version__ = `"$Version`"")) {
    throw "Version konnte nicht aktualisiert werden."
  }
  [System.IO.File]::WriteAllText($versionFile, $updatedContent, [System.Text.UTF8Encoding]::new($false))

  $pythonCandidates = @(
    (Join-Path $projectRoot ".venv\Scripts\python.exe"),
    $(if ($env:CONDA_PREFIX) { Join-Path $env:CONDA_PREFIX "python.exe" }),
    (Join-Path $HOME ".conda\envs\nemo_import_export\python.exe"),
    $((Get-Command python -ErrorAction SilentlyContinue).Source)
  ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
  $python = $pythonCandidates | Select-Object -First 1
  if (-not $python) { throw "Keine Python-Umgebung gefunden." }

  & $python -m unittest discover -s tests -v
  if ($LASTEXITCODE -ne 0) { throw "Tests fehlgeschlagen. Release wurde abgebrochen." }
  git diff --check
  if ($LASTEXITCODE -ne 0) { throw "Git-Diff enthält Formatfehler." }

  if ($BuildLocal) {
    & (Join-Path $PSScriptRoot "build-installer.ps1") -Version $Version -SkipTests
  }

  git status --short
  if (-not $Yes) {
    $confirmation = Read-Host "Alle angezeigten Änderungen als $tag committen und zu GitHub übertragen? (ja/nein)"
    if ($confirmation -notin @("ja", "j", "yes", "y")) {
      Write-Host "Release abgebrochen. Die Versionsänderung bleibt lokal erhalten."
      exit 0
    }
  }

  git add -A
  git commit -m "Release $tag"
  if ($LASTEXITCODE -ne 0) { throw "Release-Commit fehlgeschlagen." }
  git tag -a $tag -m "NEMO Deficiencies $tag"
  if ($LASTEXITCODE -ne 0) { throw "Release-Tag fehlgeschlagen." }

  $branch = (git branch --show-current).Trim()
  if (-not $branch) { throw "Aktueller Git-Branch konnte nicht ermittelt werden." }
  git push origin $branch
  if ($LASTEXITCODE -ne 0) { throw "Branch konnte nicht übertragen werden." }
  git push origin $tag
  if ($LASTEXITCODE -ne 0) { throw "Tag konnte nicht übertragen werden." }

  Write-Host "Release $tag wurde angestoßen. GitHub Actions baut Installer, Portable ZIP und Wheel."
} finally {
  Pop-Location
}
