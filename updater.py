"""Updater configuration and network helpers for GitHub Releases.

This module intentionally excludes UI code so the GUI file stays maintainable.
"""

from pathlib import Path
import json
import os
import subprocess
import time
import urllib.request
import urllib.error

ONE_CLICK_UPDATE_CONFIG = True
GITHUB_REPOSITORY = "eroisman/UTF8Converter"
GITHUB_RELEASE_EXE_ASSET_NAME = "UTF8Converter.exe"
UPDATE_CONFIG_FILE = Path(__file__).with_name("update_config.json")
GITHUB_TOKEN_ENV_VAR = "UTF8CONVERTER_GITHUB_TOKEN"
UPDATE_CHECK_TIMEOUT_SECONDS = 6
UPDATE_DOWNLOAD_TIMEOUT_SECONDS = 90
# Check updates on every app startup so users immediately see new releases.
UPDATE_CHECK_MIN_INTERVAL_SECONDS = 0
APPDATA_DIR = Path(os.getenv("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")) / "UTF8Converter"
UPDATE_STATE_PATH = APPDATA_DIR / "update_state.json"


def _version_tuple(value):
    parts = []
    for token in str(value).split("."):
        token = token.strip()
        if not token:
            parts.append(0)
            continue
        num = ""
        for char in token:
            if char.isdigit():
                num += char
            else:
                break
        parts.append(int(num) if num else 0)
    return tuple(parts)


def is_newer_version(remote_version, local_version):
    remote = _version_tuple(remote_version)
    local = _version_tuple(local_version)
    width = max(len(remote), len(local))
    remote += (0,) * (width - len(remote))
    local += (0,) * (width - len(local))
    return remote > local


def load_update_state():
    default_state = {"skipped_version": None}
    try:
        if UPDATE_STATE_PATH.exists():
            with open(UPDATE_STATE_PATH, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                default_state.update(loaded)
    except Exception:
        pass
    return default_state


def save_update_state(state):
    try:
        APPDATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(UPDATE_STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
    except Exception:
        pass


def _best_exe_asset(assets, preferred_name=""):
    if not isinstance(assets, list):
        return None
    if preferred_name:
        for asset in assets:
            if str(asset.get("name") or "").lower() == preferred_name.lower():
                return asset
    for asset in assets:
        name = str(asset.get("name") or "").lower()
        if name.endswith(".exe"):
            return asset
    return None


def _extract_sha256(asset):
    """Extract sha256 from GitHub asset metadata when available."""
    digest = str(asset.get("digest") or "").strip()
    if digest.lower().startswith("sha256:"):
        return digest.split(":", 1)[1].strip().lower()
    return ""


def fetch_manifest_from_github_release(repo_name, preferred_asset_name, app_version, github_token=""):
    repo = (repo_name or "").strip()
    if not repo or "/" not in repo:
        return None

    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"UTF8Converter/{app_version}",
    }
    token = str(github_token or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=UPDATE_CHECK_TIMEOUT_SECONDS) as response:
            release = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError(
                "GitHub API rate limit exceeded. Add a local token via "
                f"{GITHUB_TOKEN_ENV_VAR} or update_config.json -> github_token."
            ) from exc
        raise

    asset = _best_exe_asset(release.get("assets") or [], preferred_asset_name or GITHUB_RELEASE_EXE_ASSET_NAME)
    if not asset:
        return None

    tag_name = str(release.get("tag_name") or "").strip()
    version = tag_name[1:] if tag_name.lower().startswith("v") else tag_name
    if not version:
        version = str(release.get("name") or "").strip()

    return {
        "version": version,
        "name": str(release.get("name") or tag_name or version).strip(),
        "download_url": str(asset.get("browser_download_url") or "").strip(),
        "sha256": _extract_sha256(asset),
        "changelog": str(release.get("body") or "").strip(),
        "published_at": str(release.get("published_at") or "").strip(),
        "manual_url": str(release.get("html_url") or "").strip(),
    }


def download_to_file(source, destination, app_version):
    src = str(source or "").strip()
    if not src:
        raise ValueError("Missing download URL.")

    request = urllib.request.Request(
        src,
        headers={"User-Agent": f"UTF8Converter/{app_version}"},
    )
    with urllib.request.urlopen(request, timeout=UPDATE_DOWNLOAD_TIMEOUT_SECONDS) as response, open(
        destination, "wb"
    ) as fh:
        while True:
            chunk = response.read(1024 * 128)
            if not chunk:
                break
            fh.write(chunk)


def _extract_github_repo(remote_url):
    text = str(remote_url or "").strip()
    if not text:
        return ""

    if text.startswith("git@github.com:"):
        repo = text.split("git@github.com:", 1)[1]
    elif "github.com/" in text:
        repo = text.split("github.com/", 1)[1]
    else:
        return ""

    repo = repo.strip().rstrip("/")
    if repo.lower().endswith(".git"):
        repo = repo[:-4]
    if repo.count("/") != 1:
        return ""
    return repo


def _auto_detect_github_repo():
    try:
        script_dir = Path(__file__).resolve().parent
        cmd = ["git", "config", "--get", "remote.origin.url"]
        output = subprocess.check_output(cmd, cwd=str(script_dir), text=True, timeout=2)
        return _extract_github_repo(output)
    except Exception:
        return ""


def _load_update_config_file():
    if not UPDATE_CONFIG_FILE.exists():
        return {}
    try:
        with open(UPDATE_CONFIG_FILE, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return {}


def build_effective_update_config():
    """Resolve updater configuration from file/env/defaults."""
    file_config = _load_update_config_file()

    config = {
        "github_repository": str(file_config.get("github_repository") or GITHUB_REPOSITORY).strip(),
        "asset_name": str(file_config.get("asset_name") or GITHUB_RELEASE_EXE_ASSET_NAME).strip(),
        "github_token": str(os.getenv(GITHUB_TOKEN_ENV_VAR) or file_config.get("github_token") or "").strip(),
    }

    if ONE_CLICK_UPDATE_CONFIG:
        if not config["github_repository"]:
            config["github_repository"] = _auto_detect_github_repo()
        if not config["asset_name"]:
            config["asset_name"] = "UTF8Converter.exe"

    return config


def should_check_for_updates(update_state, now_epoch=None):
    """Return True when enough time elapsed since last startup check."""
    now = int(now_epoch if now_epoch is not None else time.time())
    last = int(update_state.get("last_check_epoch") or 0)
    return (now - last) >= UPDATE_CHECK_MIN_INTERVAL_SECONDS


def mark_update_check(update_state, now_epoch=None):
    """Persist timestamp of latest update check attempt."""
    now = int(now_epoch if now_epoch is not None else time.time())
    update_state["last_check_epoch"] = now
    return update_state
