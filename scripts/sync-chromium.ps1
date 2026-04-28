# scripts/sync-chromium.ps1 — fetch and sync Chromium stable into ..\chromium-src\ (Windows).
[CmdletBinding()]
param(
    [string]$Channel = 'stable'
)

$ErrorActionPreference = 'Stop'

$RepoRoot    = Resolve-Path (Join-Path $PSScriptRoot '..')
$ParentDir   = Split-Path $RepoRoot -Parent
$ChromiumSrc = Join-Path $ParentDir 'chromium-src'

if (-not (Get-Command fetch -ErrorAction SilentlyContinue)) {
    Write-Error "depot_tools not on PATH. Run scripts/bootstrap.ps1 and add depot_tools to PATH."
    exit 1
}

if (-not (Test-Path $ChromiumSrc)) { New-Item -ItemType Directory -Path $ChromiumSrc | Out-Null }
Push-Location $ChromiumSrc
try {
    if (-not (Test-Path 'src')) {
        Write-Host "==> fetching Chromium (this will take a long time)"
        & fetch chromium
    } else {
        Write-Host "==> Chromium already fetched, syncing"
        Push-Location 'src'
        & git fetch origin
        Pop-Location
        & gclient sync -r "src@refs/branch-heads/$Channel"
    }
} finally {
    Pop-Location
}

Write-Host "==> sync complete: $ChromiumSrc\src"
