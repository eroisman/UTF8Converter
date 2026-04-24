# UTF-8 Text Converter

A Windows app that converts text/subtitle files to UTF-8 and adds language suffixes for `.srt` files.

## Features

- Auto-detects file encoding
- Converts files to UTF-8
- Optional mojibake fixing (`ftfy`)
- Language detection for subtitle files (`langdetect`)
- Drag and drop file support
- Backup option (`.bak`)

## Installation

1. Download the latest release from GitHub Releases.
2. Run `UTF8Converter.exe`.

## Manual Updates

Automatic updates were removed.

To update:

1. Download the latest `UTF8Converter.exe` from Releases.
2. Replace your current executable manually.

## Developer Setup

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install chardet ftfy langdetect tkinterdnd2 pyinstaller
```

Run in development:

```powershell
python utf8_converter_gui.py
```

## Build In One Command

From the repository root:

```powershell
.\build.cmd
```

Output:

- `dist\UTF8Converter.exe`

## Versioning

Update `version.json` before building a release:

```json
{
  "version": "0.2.0",
  "name": "UTF-8 Text Converter"
}
```

## License

See `LICENSE`.
