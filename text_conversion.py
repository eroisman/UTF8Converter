"""Text/subtitle conversion and language suffix utilities.

This module contains pure conversion logic so the GUI layer can stay focused on UI.
"""

from pathlib import Path
import inspect
import shutil
import importlib
import json

import chardet
from ftfy import fix_text
from langdetect import detect_langs, DetectorFactory, LangDetectException

DetectorFactory.seed = 0  # deterministic language detection

try:
    pycountry = importlib.import_module("pycountry")
except ImportError:
    pycountry = None

DEFAULT_LANG_SUFFIXES = {
    "ar": "ara",
    "bg": "bul",
    "cs": "cze",
    "da": "dan",
    "de": "ger",
    "el": "gre",
    "en": "eng",
    "es": "spa",
    "et": "est",
    "fa": "per",
    "fi": "fin",
    "fr": "fre",
    "he": "heb",
    "hi": "hin",
    "hr": "hrv",
    "hu": "hun",
    "id": "ind",
    "is": "ice",
    "it": "ita",
    "ja": "jpn",
    "ko": "kor",
    "lt": "lit",
    "lv": "lav",
    "mk": "mac",
    "ms": "may",
    "nl": "dut",
    "no": "nor",
    "pl": "pol",
    "pt": "por",
    "ro": "rum",
    "ru": "rus",
    "sk": "slo",
    "sl": "slv",
    "sq": "alb",
    "sr": "srp",
    "sv": "swe",
    "th": "tha",
    "tr": "tur",
    "uk": "ukr",
    "ur": "urd",
    "vi": "vie",
    "zh": "chi",
    "zh-cn": "chi",
    "zh-tw": "chi",
    "pt-br": "por",
    "pt-pt": "por",
}

SUPPORTED_EXTENSIONS = {
    ".txt", ".srt", ".ass", ".ssa", ".sub", ".vtt", ".lrc",
    ".md", ".csv", ".tsv", ".ini", ".log", ".json", ".xml",
}

ENCODINGS = [
    "Auto-detect", "UTF-8", "UTF-16", "UTF-16 LE", "UTF-16 BE",
    "ISO-8859-1", "Windows-1252", "Shift_JIS", "GB18030",
]

LANGUAGE_SUFFIXES_PATH = Path(__file__).with_name("language_suffixes.json")
HAS_REMOVE_FLAG = "remove_unsafe_private_use" in inspect.signature(fix_text).parameters


def _normalize_suffix_map(raw_map):
    normalized = {}
    for key, value in raw_map.items():
        code = str(key).strip().lower()
        suffix = str(value).strip().lower()
        if code and suffix:
            normalized[code] = suffix
    return normalized


def load_language_suffixes():
    mapping = dict(DEFAULT_LANG_SUFFIXES)
    if LANGUAGE_SUFFIXES_PATH.exists():
        try:
            with open(LANGUAGE_SUFFIXES_PATH, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                mapping.update(_normalize_suffix_map(loaded))
        except Exception:
            pass
    return _normalize_suffix_map(mapping)


LANG_SUFFIXES = load_language_suffixes()


def safe_fix_text(text):
    if HAS_REMOVE_FLAG:
        return fix_text(text, remove_unsafe_private_use=False)
    return fix_text(text)


def language_to_suffix(lang_code):
    code = (lang_code or "").lower().strip()
    if not code:
        return None

    if code in LANG_SUFFIXES:
        return LANG_SUFFIXES[code]

    base_code = code.split("-")[0]
    if base_code in LANG_SUFFIXES:
        return LANG_SUFFIXES[base_code]

    if pycountry:
        language = pycountry.languages.get(alpha_2=base_code)
        if language:
            return getattr(language, "bibliographic", None) or getattr(language, "alpha_3", None)
        language = pycountry.languages.get(alpha_3=base_code)
        if language:
            return getattr(language, "bibliographic", None) or getattr(language, "alpha_3", None)

    fallback = base_code.replace("-", "_")
    return fallback if fallback else "und"


def detect_language_tag(text, snippet_len=5000, min_prob=0.60):
    snippet = text.strip()[:snippet_len]
    if not snippet:
        return None, None
    try:
        candidates = detect_langs(snippet)
    except LangDetectException:
        return None, None
    if not candidates:
        return None, None

    best = max(candidates, key=lambda c: c.prob)
    if best.prob < min_prob:
        return None, best.prob

    lang_code = best.lang.lower()
    suffix = language_to_suffix(lang_code)
    return suffix, best.prob


def append_language_suffix(path, suffix):
    if not suffix:
        return path

    stem = path.stem
    if stem.endswith(f"-{suffix}"):
        return path

    base = stem
    new_path = path.with_name(f"{base}-{suffix}{path.suffix}")
    counter = 1
    while new_path.exists():
        new_path = path.with_name(f"{base}-{suffix}_{counter}{path.suffix}")
        counter += 1

    path.rename(new_path)
    return new_path


def convert_file(file_path, make_backup, auto_fix, forced_encoding, output_folder):
    """Convert one file to UTF-8 and optionally add .srt language suffix."""
    src_path = Path(file_path)

    if output_folder:
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        target_path = output_dir / src_path.name
    else:
        target_path = src_path

    with open(src_path, "rb") as fh:
        raw = fh.read()

    if forced_encoding and forced_encoding.lower() != "auto-detect":
        encoding_used = forced_encoding
        try:
            decoded = raw.decode(encoding_used, errors="replace")
            confidence = 1.0
        except LookupError:
            decoded = raw.decode("utf-8", errors="replace")
            encoding_used = "utf-8"
            confidence = 0.0
    else:
        result = chardet.detect(raw)
        encoding_used = result.get("encoding") or "utf-8"
        confidence = result.get("confidence") or 0.0
        decoded = raw.decode(encoding_used, errors="replace")

    if auto_fix:
        decoded = safe_fix_text(decoded)

    utf8_bytes = decoded.encode("utf-8")

    if not output_folder and make_backup:
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        shutil.copy2(target_path, backup_path)

    with open(target_path, "wb") as fh:
        fh.write(utf8_bytes)

    lang_suffix, lang_prob = None, None
    if target_path.suffix.lower() == ".srt":
        lang_suffix, lang_prob = detect_language_tag(decoded)
        if lang_suffix:
            target_path = append_language_suffix(target_path, lang_suffix)

    return encoding_used, confidence, target_path, lang_suffix, lang_prob
