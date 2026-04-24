# Developer Guide

## Project Structure

- **utf8_converter_gui.py** – Main application entry point. Tkinter UI and orchestration layer.
- **text_conversion.py** – File encoding detection, UTF-8 conversion, language detection. Reusable module.
- **updater.py** – GitHub Releases integration, version checking, update mechanics. Reusable module.
- **version.json** – Version number and metadata (update this for each release).
- **language_suffixes.json** – Language code mappings for subtitle files.
- **update_config.sample.json** – Template for update source and asset configuration.

## Quick Start

```powershell
# Setup
python -m venv .venv
.venv\Scripts\python.exe -m pip install chardet ftfy langdetect tkinterdnd2 pyinstaller

# Run
python utf8_converter_gui.py

# Build
.venv\Scripts\python.exe -m PyInstaller utf8_converter_gui.spec
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
   .venv\Scripts\python.exe -m PyInstaller utf8_converter_gui.spec
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
   - Upload `dist/UTF8Converter.exe`
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

- **Update check not running?** Verify `github_repository`/`asset_name` in `update_config.json` and check for GitHub API 403 rate-limit responses.
- **File not converting?** Check encoding detection in `text_conversion.py`
- **Language not detected?** Verify `language_suffixes.json` and `langdetect` model
- **Update fails?** Check GitHub token validity and GitHub API rate limits

## Code Style

- Use type hints where helpful
- Add docstrings to functions and modules
- Keep modules focused: one responsibility each
- Test locally before building `.exe`
