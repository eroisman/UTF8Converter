# Developer Guide

## Project Structure

- **utf8_converter_gui.py** – Main application entry point. Tkinter UI and orchestration layer.
- **text_conversion.py** – File encoding detection, UTF-8 conversion, language detection. Reusable module.
- **updater.py** – GitHub Releases integration, version checking, update mechanics. Reusable module.
- **version.json** – Version number and metadata (update this for each release).
- **language_suffixes.json** – Language code mappings for subtitle files.
- **.env.example** – Template for environment variables (document, don't commit secrets).

## Quick Start

```powershell
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install chardet ftfy langdetect tkinterdnd2 pyinstaller

# Run
python utf8_converter_gui.py

# Build
pyinstaller utf8_converter_gui.spec
```

## Release Process

1. Update `version.json`:
   ```json
   {
     "version": "0.2.1",
     "name": "UTF-8 Text Converter"
   }
   ```

2. Rebuild executable:
   ```powershell
   pyinstaller utf8_converter_gui.spec
   ```

3. Test the `.exe` in `dist/` folder

4. Commit and push:
   ```powershell
   git add .
   git commit -m "Release v0.2.1"
   git push
   ```

5. Create GitHub Release:
   - Go to: https://github.com/eroisman/UTF8Converter/releases/new
   - Tag: `v0.2.1`
   - Upload `dist/utf8_converter_gui.exe`
   - Users will get automatic update notification on next app launch

## GitHub Token Setup (for CI/CD or Local Development)

Never commit tokens to git. Use environment variable:

```powershell
$env:UTF8CONVERTER_GITHUB_TOKEN = "ghp_..."
```

Or set permanently in Windows:
```powershell
[Environment]::SetEnvironmentVariable("UTF8CONVERTER_GITHUB_TOKEN", "ghp_...", "User")
```

## Debugging

- **Update check not running?** Check logs folder or enable debug mode in code
- **File not converting?** Check encoding detection in `text_conversion.py`
- **Language not detected?** Verify `language_suffixes.json` and `langdetect` model
- **Update fails?** Check GitHub token validity and GitHub API rate limits

## Code Style

- Use type hints where helpful
- Add docstrings to functions and modules
- Keep modules focused: one responsibility each
- Test locally before building `.exe`
