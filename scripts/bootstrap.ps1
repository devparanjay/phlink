# scripts/bootstrap.ps1 — install depot_tools and prepare the Chromium checkout location (Windows).
#
# Usage:
#   pwsh scripts/bootstrap.ps1 [-Force]
#
# What it does:
#   1. Clones depot_tools to %USERPROFILE%\depot_tools (if not already present).
#   2. Prints PATH setup instructions (does NOT modify your environment).
#   3. Verifies disk space and prints next steps.
#
# Refuses to run if ..\chromium-src already exists, unless -Force is passed.
[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$RepoRoot     = Resolve-Path (Join-Path $PSScriptRoot '..')
$ParentDir    = Split-Path $RepoRoot -Parent
$ChromiumSrc  = Join-Path $ParentDir 'chromium-src'
$DepotTools   = if ($env:DEPOT_TOOLS_DIR) { $env:DEPOT_TOOLS_DIR } else { Join-Path $env:USERPROFILE 'depot_tools' }

Write-Host "==> phlink bootstrap"
Write-Host "    repo:         $RepoRoot"
Write-Host "    chromium-src: $ChromiumSrc (sibling)"
Write-Host "    depot_tools:  $DepotTools"

# 1. depot_tools
if (Test-Path (Join-Path $DepotTools '.git')) {
    Write-Host "==> depot_tools already cloned at $DepotTools"
} else {
    Write-Host "==> cloning depot_tools"
    git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git $DepotTools
}

# 2. ..\chromium-src guardrail
if ((Test-Path $ChromiumSrc) -and -not $Force) {
    Write-Error "$ChromiumSrc already exists. Re-run with -Force to ignore this check."
    exit 1
}

# 3. Disk space check
$drive = (Get-Item $ParentDir).PSDrive
$freeGb = [math]::Round($drive.Free / 1GB, 1)
if ($freeGb -lt 100) {
    Write-Warning "Only $freeGb GB free on $($drive.Name):. Chromium needs ~100 GB."
}

@"

==> bootstrap complete

Next steps:

  1. Add depot_tools to your PATH for this session:

       `$env:PATH = "$DepotTools;`$env:PATH"

     Persist it in your PowerShell profile or via System Properties → Environment Variables.

  2. Fetch Chromium source (this will take a long time and a lot of disk):

       pwsh scripts/sync-chromium.ps1

  3. Generate a build directory and build:

       pwsh scripts/gn-gen.ps1
       pwsh scripts/build.ps1

  See docs/dev/build.md for the full procedure on Windows.

"@ | Write-Host
