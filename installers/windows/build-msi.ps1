# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
<#
.SYNOPSIS
  Builds a phlink MSI installer from an already-built phlink.exe tree.

.DESCRIPTION
  Wraps the WiX toolset (v3.x) to produce dist/phlink-<version>-win-x64.msi.
  Requires `candle.exe` and `light.exe` on PATH.

  This script does NOT sign the MSI. Authenticode signing is a CI step
  that runs after the EV certificate is unlocked (deferred to 10-08).

.PARAMETER OutDir
  Directory containing phlink.exe and phlink_update_helper.exe.

.PARAMETER Version
  Three-part version string (e.g. 0.1.0).
#>

param(
  [Parameter(Mandatory=$true)][string]$OutDir,
  [Parameter(Mandatory=$true)][string]$Version
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path "$OutDir/phlink.exe")) {
  throw "phlink.exe not found at $OutDir/phlink.exe"
}
if (-not (Get-Command candle.exe -ErrorAction SilentlyContinue)) {
  throw "WiX toolset not on PATH (candle.exe)."
}

$workDir = New-Item -ItemType Directory -Path "$env:TEMP/phlink-msi-$([guid]::NewGuid())"
try {
  $distDir = Join-Path (Get-Location) "dist"
  New-Item -ItemType Directory -Force -Path $distDir | Out-Null
  $wxs = @"
<?xml version='1.0' encoding='UTF-8'?>
<Wix xmlns='http://schemas.microsoft.com/wix/2006/wi'>
  <Product Id='*' Name='phlink' Manufacturer='phlink contributors'
           Version='$Version' Language='1033' UpgradeCode='B7E0F3F9-9E27-4F3E-9C5E-8C0E1B6F3A11'>
    <Package InstallScope='perUser' Compressed='yes' />
    <MediaTemplate EmbedCab='yes' />
    <MajorUpgrade DowngradeErrorMessage='A newer version of phlink is already installed.' />

    <Directory Id='TARGETDIR' Name='SourceDir'>
      <Directory Id='LocalAppDataFolder'>
        <Directory Id='INSTALLDIR' Name='phlink'>
          <Component Id='PhlinkExe' Guid='*'>
            <File Id='phlinkExe' Source='$OutDir\phlink.exe' KeyPath='yes' />
          </Component>
          <Component Id='UpdateHelper' Guid='*'>
            <File Id='phlinkUpdateHelper' Source='$OutDir\phlink_update_helper.exe' KeyPath='yes' />
          </Component>
        </Directory>
      </Directory>
    </Directory>

    <Feature Id='Main' Title='phlink' Level='1'>
      <ComponentRef Id='PhlinkExe' />
      <ComponentRef Id='UpdateHelper' />
    </Feature>
  </Product>
</Wix>
"@
  $wxsPath = Join-Path $workDir "phlink.wxs"
  $wxs | Out-File -FilePath $wxsPath -Encoding utf8

  Push-Location $workDir
  try {
    & candle.exe phlink.wxs
    if ($LASTEXITCODE -ne 0) { throw "candle failed" }
    $msiOut = Join-Path $distDir "phlink-$Version-win-x64.msi"
    & light.exe -ext WixUIExtension -out $msiOut phlink.wixobj
    if ($LASTEXITCODE -ne 0) { throw "light failed" }
    Write-Host "wrote $msiOut"
  } finally {
    Pop-Location
  }
} finally {
  Remove-Item -Recurse -Force $workDir
}
