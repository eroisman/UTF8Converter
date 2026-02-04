import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import chardet
from ftfy import fix_text
import inspect
import shutil

# --- Try to enable drag & drop (tkinterdnd2) ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    DND_FILES = None

# --- Language detection ---
from langdetect import detect_langs, DetectorFactory, LangDetectException
DetectorFactory.seed = 0  # deterministic results

LANG_SUFFIXES = {
    "he": "heb",
    "en": "eng",
    "fr": "fra",
    "es": "spa",
    "de": "deu",
    "ru": "rus",
    "ar": "ara",
    "zh-cn": "zho",
    "zh-tw": "zho_tw",
    "ja": "jpn",
    "ko": "kor",
    # Ajoutez autant de codes que nécessaire...
}

SUPPORTED_EXTENSIONS = {
    ".txt", ".srt", ".ass", ".ssa", ".sub", ".vtt", ".lrc",
    ".md", ".csv", ".tsv", ".ini", ".log", ".json", ".xml"
}
ICON_PATH = Path(__file__).with_name("utf8converter.ico")
ENCODINGS = [
    "Auto-detect", "UTF-8", "UTF-16", "UTF-16 LE", "UTF-16 BE",
    "ISO-8859-1", "Windows-1252", "Shift_JIS", "GB18030"
]

HAS_REMOVE_FLAG = "remove_unsafe_private_use" in inspect.signature(fix_text).parameters


def safe_fix_text(text):
    if HAS_REMOVE_FLAG:
        return fix_text(text, remove_unsafe_private_use=False)
    return fix_text(text)


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
    suffix = LANG_SUFFIXES.get(lang_code, lang_code.replace("-", "_"))
    return suffix, best.prob


def append_language_suffix(path, suffix):
    if not suffix:
        return path

    stem = path.stem
    if stem.endswith(f"-{suffix}"):
        return path  # déjà suffixé

    base = stem
    new_path = path.with_name(f"{base}-{suffix}{path.suffix}")
    counter = 1
    while new_path.exists():
        new_path = path.with_name(f"{base}-{suffix}_{counter}{path.suffix}")
        counter += 1

    path.rename(new_path)
    return new_path


def convert_file(file_path, make_backup, auto_fix, forced_encoding, output_folder):
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

    lang_suffix, lang_prob = detect_language_tag(decoded)
    if lang_suffix:
        target_path = append_language_suffix(target_path, lang_suffix)

    return encoding_used, confidence, target_path, lang_suffix, lang_prob


BaseClass = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk


class ConverterApp(BaseClass):
    def __init__(self):
        super().__init__()
        self.title("UTF-8 Text Converter")
        if ICON_PATH.exists():
            self.iconbitmap(ICON_PATH)
        self.geometry("780x540")
        self.resizable(False, False)

        self.backup_var = tk.BooleanVar(value=True)
        self.fix_var = tk.BooleanVar(value=True)
        self.manual_encoding = tk.StringVar(value="Auto-detect")
        self.output_folder = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Drop files or click 'Add Files' to begin.")

        self._build_ui()
        self.manual_encoding.trace_add("write", lambda *_: self._update_convert_button_label())
        self._update_convert_button_label()

        if not DND_AVAILABLE:
            self.status_var.set("Drag & drop unavailable (install tkinterdnd2).")

    def _build_ui(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        file_header = ttk.Label(container, text="Files", font=("", 11, "bold"))
        file_header.pack(anchor="w")
        button_row = ttk.Frame(container)
        button_row.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(button_row, text="Add Files", command=self.add_files).pack(side=tk.LEFT)
        ttk.Button(button_row, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_row, text="Clear All", command=self.clear_all).pack(side=tk.LEFT)

        self.listbox = tk.Listbox(container, height=10, selectmode=tk.EXTENDED)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.listbox, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        if DND_AVAILABLE:
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind("<<Drop>>", self.handle_drop)

        options_header = ttk.Label(container, text="Options", font=("", 11, "bold"))
        options_header.pack(anchor="w", pady=(12, 0))
        options_frame = ttk.Frame(container)
        options_frame.pack(fill=tk.X, pady=4)

        ttk.Checkbutton(options_frame, text="Create .bak backups before converting",
                        variable=self.backup_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(options_frame, text="Auto-fix mojibake / garbled text (ftfy)",
                        variable=self.fix_var).grid(row=1, column=0, sticky="w")

        ttk.Label(options_frame, text="Encoding override:").grid(row=0, column=1, padx=(20, 5), sticky="e")
        ttk.Combobox(options_frame, textvariable=self.manual_encoding,
                     values=ENCODINGS, width=20, state="readonly").grid(row=0, column=2, sticky="w")

        ttk.Label(options_frame, text="Output folder (optional):").grid(row=1, column=1, padx=(20, 5), sticky="e")
        out_frame = ttk.Frame(options_frame)
        out_frame.grid(row=1, column=2, sticky="we")
        out_entry = ttk.Entry(out_frame, textvariable=self.output_folder, width=28)
        out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(out_frame, text="Browse...", command=self.choose_output_folder).pack(side=tk.LEFT, padx=(4, 0))
        options_frame.columnconfigure(2, weight=1)

        log_header = ttk.Label(container, text="Activity log", font=("", 11, "bold"))
        log_header.pack(anchor="w", pady=(12, 4))
        self.log_text = tk.Text(container, height=8, wrap="word", state="disabled", bg="#f8f8f8")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        status_bar = ttk.Frame(container)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(status_bar, textvariable=self.status_var).pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(status_bar, mode="determinate", length=220)
        self.progress.pack(side=tk.RIGHT)

        self.convert_button = ttk.Button(container, command=self.start_conversion)
        self.convert_button.pack(fill=tk.X, pady=(10, 0))

    # --- Drag & drop ---
    def handle_drop(self, event):
        paths = [p for p in self.tk.splitlist(event.data) if p]
        added = 0
        for path in paths:
            if Path(path).is_file() and path not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, path)
                added += 1
        if added:
            self.status_var.set(f"{added} file(s) added via drag & drop.")

    # --- File list actions ---
    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select text or subtitle files",
            filetypes=[("Text & subtitle files", ";".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)),
                       ("All files", "*.*")]
        )
        for p in paths:
            if p not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, p)

    def remove_selected(self):
        for index in reversed(self.listbox.curselection()):
            self.listbox.delete(index)

    def clear_all(self):
        self.listbox.delete(0, tk.END)

    def choose_output_folder(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_folder.set(folder)

    # --- Conversion flow ---
    def start_conversion(self):
        files = self.listbox.get(0, tk.END)
        if not files:
            messagebox.showinfo("No files", "Please add files to convert.")
            return

        self.convert_button.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.progress["maximum"] = len(files)
        self.status_var.set("Converting...")
        self._log("Starting conversion...\n", clear=True)

        worker = threading.Thread(target=self._convert_batch, args=(files,), daemon=True)
        worker.start()

    def _convert_batch(self, files):
        success = 0
        for index, file_path in enumerate(files, start=1):
            try:
                encoding, confidence, target, lang_suffix, lang_prob = convert_file(
                    file_path=file_path,
                    make_backup=self.backup_var.get(),
                    auto_fix=self.fix_var.get(),
                    forced_encoding=self.manual_encoding.get(),
                    output_folder=self.output_folder.get().strip() or None
                )
                lang_info = f" | lang={lang_suffix} ({lang_prob:.2f})" if lang_suffix else ""
                self._log(f"[OK] {Path(file_path).name}: {encoding} ({confidence:.2f}) → {target}{lang_info}\n")
                success += 1
            except Exception as exc:
                self._log(f"[ERROR] {Path(file_path).name}: {exc}\n")
            self._update_progress(index)

        self._finish_conversion(success, len(files))

    def _finish_conversion(self, success, total):
        def finalize():
            self.convert_button.config(state=tk.NORMAL)
            self.status_var.set(f"Done. {success}/{total} files converted.")
            messagebox.showinfo("Conversion complete", f"{success}/{total} files converted.")
        self.after(0, finalize)

    # --- UI helpers ---
    def _log(self, message, clear=False):
        def write():
            self.log_text.configure(state="normal")
            if clear:
                self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, message)
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
        self.after(0, write)

    def _update_progress(self, value):
        self.after(0, lambda: self.progress.config(value=value))

    def _update_convert_button_label(self):
        selected = self.manual_encoding.get()
        if selected and selected != "Auto-detect":
            self.convert_button.config(text=f"Convert to UTF-8 (force: {selected})")
        else:
            self.convert_button.config(text="Convert to UTF-8")


if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
