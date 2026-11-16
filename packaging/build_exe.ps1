<#
.SYNOPSIS
    在本机打包 paiban 的 Windows 可执行文件。

.EXAMPLE
    .\packaging\build_exe.ps1            # 单文件 dist\paiban.exe
    .\packaging\build_exe.ps1 -OneDir    # 目录版 dist\paiban\paiban.exe（启动更快）
#>
param([switch]$OneDir)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "==> 检查 PyInstaller"
python -m PyInstaller --version
if ($LASTEXITCODE -ne 0) {
    throw "没装 PyInstaller，请先执行：python -m pip install pyinstaller"
}

$mode = if ($OneDir) { "--onedir" } else { "--onefile" }

Push-Location $root
try {
    Write-Host "==> 打包（$mode）"
    python -m PyInstaller --noconfirm --clean $mode `
        --name paiban --paths src packaging/paiban_win.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller 打包失败" }

    $exe = if ($OneDir) { "dist\paiban\paiban.exe" } else { "dist\paiban.exe" }
    Write-Host "==> 完成：$root\$exe"
} finally {
    Pop-Location
}
