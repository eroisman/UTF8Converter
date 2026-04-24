$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    $pythonExe = ".venv\Scripts\python.exe"

    if (-not (Test-Path $pythonExe)) {
        python -m venv .venv
    }

    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install chardet ftfy langdetect tkinterdnd2 pyinstaller

    if (Test-Path ".\build") {
        Remove-Item ".\build" -Recurse -Force
    }
    if (Test-Path ".\dist") {
        Remove-Item ".\dist" -Recurse -Force
    }

    & $pythonExe -m PyInstaller --clean --noconfirm utf8_converter_gui.spec

    Write-Host "Build complete: dist\UTF8Converter.exe"
}
finally {
    Pop-Location
}
