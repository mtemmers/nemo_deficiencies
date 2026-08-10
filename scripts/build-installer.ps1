[CmdletBinding()]
param(
  [string]$Version,
  [switch]$SkipTests,
  [switch]$SkipInstaller,
  [switch]$SkipDependencyInstall,
  [switch]$PreserveRelease
)

$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$versionFile = Join-Path $projectRoot "backend\__init__.py"
$versionMatch = [regex]::Match(
  [System.IO.File]::ReadAllText($versionFile),
  '__version__\s*=\s*"(?<version>\d+\.\d+\.\d+)"'
)
if (-not $versionMatch.Success) {
  throw "Die Anwendungsversion konnte nicht aus backend\__init__.py gelesen werden."
}
$applicationVersion = $versionMatch.Groups["version"].Value
if (-not $Version) {
  $Version = $applicationVersion
}
$Version = $Version.TrimStart("v")
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
  throw "Ungültige Version '$Version'. Erwartet wird beispielsweise 1.4.0."
}
if ($Version -ne $applicationVersion) {
  throw "Version $Version stimmt nicht mit backend\__init__.py ($applicationVersion) überein."
}

$pythonCandidates = @(
  (Join-Path $projectRoot ".venv\Scripts\python.exe"),
  $(if ($env:CONDA_PREFIX) { Join-Path $env:CONDA_PREFIX "python.exe" }),
  (Join-Path $HOME ".conda\envs\nemo_import_export\python.exe"),
  $((Get-Command python -ErrorAction SilentlyContinue).Source)
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
$python = $null
foreach ($candidate in $pythonCandidates) {
  if ($SkipDependencyInstall) {
    & $candidate -c "import build, fastapi, nemo_library, PyInstaller, uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) {
      continue
    }
  }
  $python = $candidate
  break
}
if (-not $python) {
  $hint = if ($SkipDependencyInstall) {
    "Keine Python-Umgebung mit allen Build-Abhängigkeiten gefunden. Erneut ohne -SkipDependencyInstall starten."
  } else {
    "Keine Python-Umgebung gefunden."
  }
  throw $hint
}
Write-Host "Build-Python: $python"

Push-Location $projectRoot
try {
  if (-not $SkipDependencyInstall) {
    & $python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip konnte nicht aktualisiert werden." }
    & $python -m pip install -e . -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw "Build-Abhängigkeiten konnten nicht installiert werden." }
  }

  if (-not $SkipTests) {
    & $python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Tests fehlgeschlagen." }
  }

  $buildTargets = @(
    (Join-Path $projectRoot "build"),
    (Join-Path $projectRoot "dist")
  )
  if (-not $PreserveRelease) {
    $buildTargets += (Join-Path $projectRoot "release")
  }
  $rootPrefix = $projectRoot.TrimEnd("\") + "\"
  foreach ($target in $buildTargets) {
    $absoluteTarget = [System.IO.Path]::GetFullPath($target)
    if (-not $absoluteTarget.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
      throw "Unsicheres Build-Ziel erkannt: $absoluteTarget"
    }
    if (Test-Path -LiteralPath $absoluteTarget) {
      Remove-Item -LiteralPath $absoluteTarget -Recurse -Force
    }
  }
  New-Item -ItemType Directory -Path (Join-Path $projectRoot "release") -Force | Out-Null

  & $python -m PyInstaller --noconfirm --clean nemo_deficiencies.spec
  if ($LASTEXITCODE -ne 0) { throw "PyInstaller-Build fehlgeschlagen." }

  $portableZip = Join-Path $projectRoot "release\NEMO-Deficiencies-$Version-portable.zip"
  Compress-Archive -Path (Join-Path $projectRoot "dist\NEMO Deficiencies\*") -DestinationPath $portableZip -CompressionLevel Optimal

  & $python -m build --wheel --outdir (Join-Path $projectRoot "release")
  if ($LASTEXITCODE -ne 0) { throw "Python-Wheel konnte nicht gebaut werden." }

  if (-not $SkipInstaller) {
    $isccCandidates = @(
      "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
      "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
      "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $iscc = $isccCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $iscc) {
      throw "Inno Setup 6 wurde nicht gefunden. Installation: winget install JRSoftware.InnoSetup"
    }
    & $iscc "/DAppVersion=$Version" (Join-Path $projectRoot "installer\nemo_deficiencies.iss")
    if ($LASTEXITCODE -ne 0) { throw "Installer-Build fehlgeschlagen." }
  }

  $releaseFiles = Get-ChildItem -LiteralPath (Join-Path $projectRoot "release") -File |
    Where-Object { $_.Name -ne "SHA256SUMS.txt" -and $_.Name -like "*$Version*" }
  $checksums = foreach ($file in $releaseFiles) {
    $hash = Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
    "$($hash.Hash.ToLowerInvariant())  $($file.Name)"
  }
  [System.IO.File]::WriteAllLines(
    (Join-Path $projectRoot "release\SHA256SUMS.txt"),
    $checksums,
    [System.Text.UTF8Encoding]::new($false)
  )

  Write-Host ""
  Write-Host "Release $Version wurde erstellt:"
  Get-ChildItem -LiteralPath (Join-Path $projectRoot "release") -File |
    Select-Object Name, Length |
    Format-Table -AutoSize
} finally {
  Pop-Location
}
