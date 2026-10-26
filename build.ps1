param(
    [string]$Target = "$PSScriptRoot\dist\TranslateOffline",
    [string[]]$Languages = @(),
    [switch]$Installer
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$PyVersion = "3.11.9"

if (Test-Path "$Target\python") { Remove-Item "$Target\python" -Recurse -Force }
New-Item -ItemType Directory -Force "$Target\python", "$Target\data" | Out-Null
$py = "$Target\python\python.exe"

Write-Host "[1/5] Downloading portable Python $PyVersion..."
$zip = Join-Path $env:TEMP "python-$PyVersion-embed-amd64.zip"
Invoke-WebRequest "https://www.python.org/ftp/python/$PyVersion/python-$PyVersion-embed-amd64.zip" -OutFile $zip
Expand-Archive $zip "$Target\python" -Force
Set-Content "$Target\python\python311._pth" -Encoding ascii -Value "python311.zip`r`n.`r`nLib\site-packages`r`nimport site"

Write-Host "[2/5] Installing pip..."
$getPip = Join-Path $env:TEMP "get-pip.py"
Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip
& $py $getPip --no-warn-script-location

Write-Host "[3/5] Installing translation engine and window toolkit..."
& $py -m pip install argos-translate-lt langdetect pywebview --no-warn-script-location

foreach ($dll in "msvcp140.dll", "msvcp140_1.dll", "msvcp140_2.dll", "vcruntime140.dll", "vcruntime140_1.dll", "concrt140.dll", "vcomp140.dll") {
    $src = Join-Path "$env:SystemRoot\System32" $dll
    if (Test-Path $src) { Copy-Item $src "$Target\python\" -Force }
}
Copy-Item "$PSScriptRoot\app.py", "$PSScriptRoot\assets\icon.ico" $Target -Force

Write-Host "[4/5] Downloading language models..."
$data = "$Target\data"
$env:HOME = $data
$env:XDG_DATA_HOME = "$data\share"
$env:XDG_CACHE_HOME = "$data\cache"
$env:XDG_CONFIG_HOME = "$data\config"
$env:ARGOS_PACKAGES_DIR = "$data\share\argos-translate\packages"
& $py "$PSScriptRoot\download-models.py" @Languages
Remove-Item "$data\cache", "$data\config" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Portable folder ready: $Target"

if ($Installer) {
    Write-Host "[5/5] Building installer..."
    $redist = "$PSScriptRoot\dist\redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"
    if (-not (Test-Path $redist)) {
        New-Item -ItemType Directory -Force (Split-Path $redist) | Out-Null
        Invoke-WebRequest "https://go.microsoft.com/fwlink/?linkid=2124701" -OutFile $redist
    }
    $iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) { throw "Inno Setup 6 not found. Install it with: winget install JRSoftware.InnoSetup" }
    & $iscc "/DSourceDir=$Target" "$PSScriptRoot\installer.iss"
    Write-Host "Installer ready in $PSScriptRoot\dist"
}
