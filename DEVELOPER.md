# Developer Guide

## Project Structure

- `utf8_converter_gui.py` - Main UI app.
- `text_conversion.py` - Conversion and language-suffix logic.
- `version.json` - App version metadata.
- `language_suffixes.json` - Language code to suffix mapping.
- `utf8_converter_gui.spec` - PyInstaller build spec.
- `build.ps1` - One-command clean rebuild script.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install chardet ftfy langdetect tkinterdnd2 pyinstaller
python utf8_converter_gui.py
```

## Build

```powershell
.\build.cmd
```

Produces:

- `dist\UTF8Converter.exe`

## Release Process

1. Update `version.json`.
2. Run `.\build.cmd`.
3. Test `dist\UTF8Converter.exe`.
4. Create a GitHub release and upload `dist\UTF8Converter.exe`.

## Notes

- Automatic update code has been removed.
- Users must update by downloading a new executable manually.
