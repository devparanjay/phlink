# scripts/gn-gen.ps1 — generate a Chromium build dir using phlink's GN args baseline (Windows).
[CmdletBinding()]
param(
    [string]$OutDir = 'out\Default'
)

$ErrorActionPreference = 'Stop'

$RepoRoot     = Resolve-Path (Join-Path $PSScriptRoot '..')
$ParentDir    = Split-Path $RepoRoot -Parent
$ChromiumSrc  = Join-Path $ParentDir 'chromium-src\src'
$CommonFile   = Join-Path $RepoRoot 'build\gn-args\common.gni'
$PlatformFile = Join-Path $RepoRoot 'build\gn-args\win.gn'

if (-not (Test-Path $ChromiumSrc)) {
    Write-Error "Chromium source not found at $ChromiumSrc. Run scripts/sync-chromium.ps1 first."
    exit 1
}
if (-not (Get-Command gn -ErrorAction SilentlyContinue)) {
    Write-Error "gn not on PATH. Make sure depot_tools is on PATH."
    exit 1
}

$lines = @()
$lines += Get-Content $CommonFile
$lines += Get-Content $PlatformFile
$args = ($lines | ForEach-Object { ($_ -replace '#.*$','').Trim() } | Where-Object { $_ }) -join ' '

Write-Host "==> generating $ChromiumSrc\$OutDir with args from $CommonFile + $PlatformFile"
Push-Location $ChromiumSrc
try {
    & gn gen $OutDir --args="$args"
} finally {
    Pop-Location
}
