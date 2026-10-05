import re
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "SA Display Manager"
OUTPUT_NAME = "Sa-Display-Manager.exe"

URLS = [
    ("Main Dashboard", "https://nwsmatthewclay.github.io/NWS_SA_Dashboard/"),
    ("Calendar", "https://nwsmatthewclay.github.io/NWS_SA_Dashboard/calendar.html"),
    ("Recreation", "https://nwsmatthewclay.github.io/NWS_SA_Dashboard/recreation.html"),
    ("Mountain", "https://nwsmatthewclay.github.io/NWS_SA_Dashboard/mountain.html"),
    ("Products", "https://nwsmatthewclay.github.io/NWS_SA_Dashboard/products.html"),
    ("Verification", "https://nwsmatthewclay.github.io/NWS_SA_Dashboard/verification.html"),
]

DEFAULT_SECONDS = 20


class DisplayManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.resizable(False, False)
        self.configure(padx=18, pady=18)

        self.path_var = tk.StringVar()
        self.seconds_var = tk.StringVar(value=str(DEFAULT_SECONDS))
        self.status_var = tk.StringVar(value="Select whiteboard.php, choose your pages, then save.")

        self.vars = []
        self._build()

    def _build(self):
        ttk.Label(self, text=APP_NAME, font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            self,
            text="Configure the SA display slideshow by editing whiteboard.php.",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        ttk.Label(self, text="PHP file").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.path_var, width=62).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(4, 10)
        )
        ttk.Button(self, text="Browse…", command=self.browse).grid(
            row=3, column=2, padx=(8, 0), pady=(4, 10)
        )

        ttk.Label(self, text="Rotation interval (seconds)").grid(
            row=4, column=0, sticky="w"
        )
        ttk.Spinbox(
            self,
            from_=1,
            to=86400,
            textvariable=self.seconds_var,
            width=10,
        ).grid(row=5, column=0, sticky="w", pady=(4, 12))

        ttk.Label(self, text="Websites to display", font=("Segoe UI", 11, "bold")).grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(2, 6)
        )

        for i, (name, url) in enumerate(URLS):
            var = tk.BooleanVar(value=i < 5)
            self.vars.append(var)
            cb = ttk.Checkbutton(self, text=name, variable=var)
            cb.grid(row=7 + i, column=0, columnspan=3, sticky="w", pady=2)
            ttk.Label(
                self, text=url, foreground="#666666", font=("Segoe UI", 8)
            ).grid(row=7 + i, column=1, columnspan=2, sticky="w", padx=(18, 0), pady=2)

        ttk.Button(self, text="Select All", command=self.select_all).grid(
            row=14, column=0, sticky="w", pady=(12, 0)
        )
        ttk.Button(self, text="Clear All", command=self.clear_all).grid(
            row=14, column=1, sticky="w", padx=(8, 0), pady=(12, 0)
        )
        ttk.Button(self, text="Update PHP", command=self.update_php).grid(
            row=14, column=2, sticky="e", pady=(12, 0)
        )

        ttk.Separator(self).grid(row=15, column=0, columnspan=3, sticky="ew", pady=14)
        ttk.Label(self, textvariable=self.status_var, wraplength=580).grid(
            row=16, column=0, columnspan=3, sticky="w"
        )

    def browse(self):
        path = filedialog.askopenfilename(
            title="Select whiteboard.php",
            filetypes=[("PHP files", "*.php"), ("All files", "*.*")],
        )
        if path:
            self.path_var.set(path)
            self.status_var.set(f"Selected: {path}")

    def select_all(self):
        for var in self.vars:
            var.set(True)

    def clear_all(self):
        for var in self.vars:
            var.set(False)

    def update_php(self):
        path_text = self.path_var.get().strip()
        if not path_text:
            messagebox.showerror(APP_NAME, "Please select whiteboard.php first.")
            return

        php_path = Path(path_text)
        if not php_path.is_file():
            messagebox.showerror(APP_NAME, f"File not found:\n{php_path}")
            return

        try:
            seconds = int(self.seconds_var.get())
        except ValueError:
            messagebox.showerror(APP_NAME, "Rotation interval must be a whole number.")
            return

        if seconds < 1:
            messagebox.showerror(APP_NAME, "Rotation interval must be at least 1 second.")
            return

        selected = [
            url for (name, url), var in zip(URLS, self.vars) if var.get()
        ]
        if not selected:
            messagebox.showerror(APP_NAME, "Select at least one website.")
            return

        try:
            original = php_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                original = php_path.read_text(encoding="cp1252")
            except Exception as exc:
                messagebox.showerror(APP_NAME, f"Could not read PHP file:\n{exc}")
                return
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not read PHP file:\n{exc}")
            return

        updated = self._replace_urls(original, selected)
        if updated is None:
            messagebox.showerror(
                APP_NAME,
                "Could not locate the $url array in whiteboard.php. "
                "The file structure may differ from the expected SA display format.",
            )
            return

        updated = self._replace_refresh_interval(updated, seconds)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = php_path.with_name(f"{php_path.name}.bak_{timestamp}")

        try:
            shutil.copy2(php_path, backup)
            php_path.write_text(updated, encoding="utf-8", newline="")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not update PHP file:\n{exc}")
            return

        self.status_var.set(
            f"Updated successfully. Backup created:\n{backup}"
        )
        messagebox.showinfo(
            APP_NAME,
            f"SA display updated successfully.\n\n"
            f"Pages enabled: {len(selected)}\n"
            f"Rotation: {seconds} seconds\n\n"
            f"Backup:\n{backup}",
        )

    @staticmethod
    def _replace_urls(text, urls):
        # Replace only the fixed $url[0]...$url[n] entries while leaving the
        # dynamic PNG logic and all other PHP intact.
        array_start = text.find("$url = array();")
        if array_start == -1:
            return None

        replacements = []
        for i, url in enumerate(urls):
            replacements.append(f'    $url[{i}] = "{url}";')

        # Preserve/replace a contiguous block of indexed URL assignments.
        pattern = re.compile(
            r"(?ms)(\$url\s*=\s*array\(\);\s*)"
            r"(?:\s*\$url\[\d+\]\s*=\s*.*?;)+"
        )

        match = pattern.search(text, array_start)
        if not match:
            return None

        new_block = match.group(1) + "\n" + "\n".join(replacements) + "\n"
        return text[:match.start()] + new_block + text[match.end():]

    @staticmethod
    def _replace_refresh_interval(text, seconds):
        # The original whiteboard.php has CONTENT="20;URL=...".
        return re.sub(
            r'(<META\s+HTTP-EQUIV="refresh"\s*\n?\s*CONTENT=")\d+(;URL=)',
            rf"\g<1>{seconds}\g<2>",
            text,
            flags=re.IGNORECASE,
        )


if __name__ == "__main__":
    app = DisplayManager()
    app.mainloop()
