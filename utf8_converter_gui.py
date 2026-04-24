import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import sys
import json

from text_conversion import ENCODINGS, SUPPORTED_EXTENSIONS, convert_file

# --- Try to enable drag & drop (tkinterdnd2) ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    DND_FILES = None

ICON_PATH = Path(__file__).with_name("utf8converter.ico")


def _version_file_candidates():
    """Return likely version.json locations for source and packaged runs."""
    candidates = []

    # Source mode: version.json beside this script.
    candidates.append(Path(__file__).with_name("version.json"))

    # Packaged mode: version.json beside the executable.
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).with_name("version.json"))

    # PyInstaller one-file extraction directory.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "version.json")

    # De-duplicate while preserving order.
    unique = []
    seen = set()
    for path in candidates:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def _load_app_version():
    """Load version from version.json, fallback to 0.1.0 if not found."""
    for version_file in _version_file_candidates():
        try:
            if not version_file.exists():
                continue
            with open(version_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            version = str(data.get("version", "")).strip()
            if version:
                return version
        except Exception:
            continue
    return "0.1.0"


APP_VERSION = _load_app_version()


BaseClass = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk


class ConverterApp(BaseClass):
    """Tkinter UI shell for file conversion workflows."""

    # GUI orchestration only: conversion business logic is delegated to modules.
    def __init__(self):
        super().__init__()
        self.title("UTF-8 Text Converter")
        if ICON_PATH.exists():
            self.iconbitmap(ICON_PATH)
        self.geometry("780x540")
        self.resizable(False, False)

        self.backup_var = tk.BooleanVar(value=False)
        self.fix_var = tk.BooleanVar(value=True)
        self.manual_encoding = tk.StringVar(value="Auto-detect")
        self.output_folder = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Drop files or click 'Add Files' to begin.")
        self.backup_hint_tip = None
        self.backup_hint_pinned = False

        self._build_ui()
        self.manual_encoding.trace_add("write", lambda *_: self._update_convert_button_label())
        self._update_convert_button_label()

        if not DND_AVAILABLE:
            self.status_var.set("Drag & drop unavailable (install tkinterdnd2).")

        self._log(f"[INFO] UTF-8 Text Converter version {APP_VERSION}\n")

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

        backup_row = ttk.Frame(options_frame)
        backup_row.grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(backup_row, text="Create .bak backups before converting",
                variable=self.backup_var).pack(side=tk.LEFT)
        backup_hint = ttk.Label(backup_row, text="ⓘ", foreground="#0a5fb4", cursor="hand2")
        backup_hint.pack(side=tk.LEFT, padx=(6, 0))
        backup_hint.bind("<Enter>", self._show_backup_hint)
        backup_hint.bind("<Leave>", self._hide_backup_hint)
        backup_hint.bind("<Button-1>", self._toggle_backup_hint)
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

    def _show_backup_hint(self, event=None):
        widget = event.widget if event else self
        if self.backup_hint_tip and self.backup_hint_tip.winfo_exists():
            return

        x = widget.winfo_rootx() + widget.winfo_width() + 10
        y = widget.winfo_rooty() - 4

        tip = tk.Toplevel(self)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tip,
            text="Optional. Backups are disabled by default.\nEnable only if you want .bak copies.",
            bg="#fff8dc",
            fg="#222222",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=5,
            justify="left"
        )
        label.pack()
        self.backup_hint_tip = tip

    def _hide_backup_hint(self, _event=None):
        if self.backup_hint_pinned:
            return
        if self.backup_hint_tip and self.backup_hint_tip.winfo_exists():
            self.backup_hint_tip.destroy()
        self.backup_hint_tip = None

    def _toggle_backup_hint(self, event):
        if self.backup_hint_tip and self.backup_hint_tip.winfo_exists():
            if self.backup_hint_pinned:
                self.backup_hint_pinned = False
                self._hide_backup_hint()
            else:
                self.backup_hint_pinned = True
            return

        self.backup_hint_pinned = True
        self._show_backup_hint(event)

if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
