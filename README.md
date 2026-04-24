# UTF-8 Text Converter

A simple Windows application that converts text files and subtitles to UTF-8 encoding with automatic language detection for subtitle files.

## Features

- ✅ **Auto-detects encoding** – Automatically identifies the encoding of your files
- ✅ **Converts to UTF-8** – Reliably converts any text file to UTF-8
- ✅ **Fixes text corruption** – Automatically corrects mojibake and other text issues
- ✅ **Language detection for subtitles** – Automatically detects language and renames `.srt` files (e.g., `movie-eng.srt`, `movie-heb.srt`)
- ✅ **Drag & drop support** – Simply drag files onto the window
- ✅ **File type support** – Works with `.txt`, `.srt`, `.ass`, `.vtt`, `.md`, `.csv`, and more
- ✅ **Backup option** – Creates `.bak` backups of original files
- ✅ **Progress tracking** – See conversion progress with a progress bar and log
- ✅ **In-app auto update popup** – On startup, the app checks GitHub Releases and offers one-click update + relaunch

## Installation

1. Download the latest release from [GitHub Releases](https://github.com/eroisman/UTF8Converter/releases)
2. Run `UTF8Converter.exe`

That's it! No configuration needed.

## How to Use

1. **Open the application** – Run `UTF8Converter.exe`
2. **Select files** – Click "Select Files" or drag files onto the window
3. **Configure** (optional):
   - Select input encoding (auto-detect is recommended)
   - Choose output folder
   - Enable backup to save originals
   - Enable text fixing (remove character corruption)
4. **Convert** – Click "Convert" and wait for completion
5. **Check results** – Converted files appear in the output folder

### For Subtitle Files (`.srt`)

After conversion, files are automatically renamed with language suffix:
- `subtitle.srt` → `subtitle-eng.srt` (English)
- `subtitle.srt` → `subtitle-heb.srt` (Hebrew)
- etc.

This is compatible with MKVToolNix and most media players.

## For Developers

### Prerequisites

- Python 3.11+
- Dependencies: `chardet`, `ftfy`, `langdetect`, `tkinterdnd2`

### Setup

```powershell
# Clone the repository
git clone https://github.com/eroisman/UTF8Converter.git
cd UTF8Converter

# Create virtual environment
python -m venv .venv

# Install dependencies
.venv\Scripts\python.exe -m pip install chardet ftfy langdetect tkinterdnd2 pyinstaller
```

### Run in Development

```powershell
python utf8_converter_gui.py
```

### Build Executable

```powershell
.venv\Scripts\python.exe -m PyInstaller utf8_converter_gui.spec
```

The `.exe` will be created in `dist/` folder.

## Automatic Updates

The app checks GitHub Releases when it starts. If a newer version exists, users get an update popup with release notes and three options:

- **Update**: download, replace current `.exe`, and relaunch automatically
- **Remind me later**
- **Skip this version**

To configure repository/asset or provide a token:

### Method 1: Environment Variable (Recommended)

Set an environment variable with your GitHub token:

```powershell
$env:UTF8CONVERTER_GITHUB_TOKEN = "your_github_token_here"
```

Make this permanent in Windows:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** → **Environment Variables**
3. Click **New** under User variables
4. Variable name: `UTF8CONVERTER_GITHUB_TOKEN`
5. Variable value: `your_github_token_here`
6. Click OK

### Method 2: Local Config File

Create `update_config.json` in the same folder as the `.exe`:

```json
{
  "github_repository": "eroisman/UTF8Converter",
   "asset_name": "UTF8Converter.exe",
  "github_token": ""
}
```

> **Note**: Leave `github_token` empty to use the environment variable. If you leave it empty and have no token, update checks still run, but may occasionally fail if GitHub API rate limits are reached.

### How to Get a GitHub Token

1. Go to https://github.com/settings/tokens/new
2. Select scope: `public_repo` (read-only access to public repositories)
3. Generate and copy the token
4. Set it in the environment variable or config file

## Version Management

To release a new version:

1. Update the version in `version.json`:
   ```json
   {
     "version": "0.2.0",
     "name": "UTF-8 Text Converter"
   }
   ```

2. Rebuild the `.exe`:
   ```powershell
   .venv\Scripts\python.exe -m PyInstaller utf8_converter_gui.spec
   ```

3. Upload to GitHub Releases

The app will automatically detect the new version and offer to update.

## License

See [LICENSE](LICENSE) file for details.
