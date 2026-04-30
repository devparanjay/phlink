# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
<#
.SYNOPSIS
  Builds a phlink MSI installer from an already-built phlink.exe tree.

.DESCRIPTION
  Wraps the WiX toolset (v3.x) to produce dist/phlink-<version>-win-x64.msi.
  Requires `candle.exe` and `light.exe` on PATH.

  When CertificatePath is provided, signs phlink.exe,
  phlink_update_helper.exe, and the generated MSI with Authenticode and
  verifies each signature.

.PARAMETER OutDir
  Directory containing phlink.exe and phlink_update_helper.exe.

.PARAMETER Version
  Three-part version string (e.g. 0.1.0).

.PARAMETER CertificatePath
  Optional Authenticode signing certificate PFX path.

.PARAMETER CertificatePassword
  Password for CertificatePath.

.PARAMETER TimestampUrl
  RFC 3161 timestamp server URL for Authenticode signing.
#>

param(
  [Parameter(Mandatory=$true)][string]$OutDir,
  [Parameter(Mandatory=$true)][string]$Version,
  [string]$CertificatePath = "",
  [string]$CertificatePassword = "",
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path "$OutDir/phlink.exe")) {
  throw "phlink.exe not found at $OutDir/phlink.exe"
}
if (-not (Test-Path "$OutDir/phlink_update_helper.exe")) {
  throw "phlink_update_helper.exe not found at $OutDir/phlink_update_helper.exe"
}
if (-not (Get-Command candle.exe -ErrorAction SilentlyContinue)) {
  throw "WiX toolset not on PATH (candle.exe)."
}
if (-not (Get-Command heat.exe -ErrorAction SilentlyContinue)) {
  throw "WiX toolset not on PATH (heat.exe)."
}

$signtool = $null
if ($CertificatePath -ne "") {
  if (-not (Test-Path $CertificatePath)) {
    throw "signing certificate not found at $CertificatePath"
  }
  if ($CertificatePassword -eq "") {
    throw "CertificatePassword is required when CertificatePath is provided."
  }
  $signtool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" `
      -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1
  if ($null -eq $signtool) {
    throw "signtool.exe not found in Windows Kits."
  }
}

function Sign-And-Verify([string]$Path) {
  if ($null -eq $signtool) { return }
  & $signtool.FullName sign /fd SHA256 /td SHA256 /tr $TimestampUrl `
    /f $CertificatePath /p $CertificatePassword $Path
  if ($LASTEXITCODE -ne 0) { throw "signtool sign failed for $Path" }
  & $signtool.FullName verify /pa /v $Path
  if ($LASTEXITCODE -ne 0) { throw "signtool verify failed for $Path" }
}

Sign-And-Verify "$OutDir/phlink.exe"
Sign-And-Verify "$OutDir/phlink_update_helper.exe"

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
        <Directory Id='INSTALLDIR' Name='phlink' />
      </Directory>
    </Directory>

    <Feature Id='Main' Title='phlink' Level='1'>
      <ComponentGroupRef Id='PhlinkFiles' />
    </Feature>
  </Product>
</Wix>
"@
  $wxsPath = Join-Path $workDir "phlink.wxs"
  $wxs | Out-File -FilePath $wxsPath -Encoding utf8

  Push-Location $workDir
  try {
    & heat.exe dir $OutDir -cg PhlinkFiles -dr INSTALLDIR -srd -sreg -gg `
      -var var.OutDir -out phlink-files.wxs
    if ($LASTEXITCODE -ne 0) { throw "heat failed" }
    & candle.exe -dOutDir="$OutDir" phlink.wxs phlink-files.wxs
    if ($LASTEXITCODE -ne 0) { throw "candle failed" }
    $msiOut = Join-Path $distDir "phlink-$Version-win-x64.msi"
    & light.exe -ext WixUIExtension -out $msiOut phlink.wixobj phlink-files.wixobj
    if ($LASTEXITCODE -ne 0) { throw "light failed" }
    Sign-And-Verify $msiOut
    Write-Host "wrote $msiOut"
  } finally {
    Pop-Location
  }
} finally {
  Remove-Item -Recurse -Force $workDir
}
