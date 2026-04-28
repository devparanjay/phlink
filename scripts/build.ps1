# scripts/build.ps1 — build phlink (Windows).
[CmdletBinding()]
param(
    [string]$OutDir = 'out\Default',
    [string]$Target = 'chrome'
)

$ErrorActionPreference = 'Stop'

$RepoRoot    = Resolve-Path (Join-Path $PSScriptRoot '..')
$ParentDir   = Split-Path $RepoRoot -Parent
$ChromiumSrc = Join-Path $ParentDir 'chromium-src\src'

if (-not (Get-Command autoninja -ErrorAction SilentlyContinue)) {
    Write-Error "autoninja not on PATH. Make sure depot_tools is on PATH."
    exit 1
}

Push-Location $ChromiumSrc
try {
    Write-Host "==> autoninja -C $OutDir $Target"
    & autoninja -C $OutDir $Target
} finally {
    Pop-Location
}
