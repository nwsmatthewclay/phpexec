import re
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "SA Display Manager"

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
        self.geometry("620x520")
        self.configure(bg="#eef3f8")
        self.option_add("*Font", ("Segoe UI", 10))

        self.path_var = tk.StringVar(value="whiteboard.php")
        self.seconds_var = tk.StringVar(value=str(DEFAULT_SECONDS))
        self.status_var = tk.StringVar(value="Ready to configure the SA display.")
        self.vars = [tk.BooleanVar(value=i < 5) for i in range(len(URLS))]

        self._build()

    def _build(self):
        self.configure(padx=0, pady=0)

        header = tk.Frame(self, bg="#123b5d", height=86)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="SA DISPLAY MANAGER",
            bg="#123b5d", fg="white",
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", padx=24, pady=(16, 0))
        tk.Label(
            header, text="Configure the Science & Aviation display rotation",
            bg="#123b5d", fg="#cfe5f5",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=25, pady=(2, 0))

        body = tk.Frame(self, bg="#eef3f8")
        body.pack(fill="both", expand=True, padx=18, pady=16)

        # Fixed target card
        target = tk.Frame(body, bg="white", highlightbackground="#d5dee8", highlightthickness=1)
        target.pack(fill="x", pady=(0, 10))
        tk.Label(target, text="DISPLAY FILE", bg="white", fg="#5a6b7b",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        row = tk.Frame(target, bg="white")
        row.pack(fill="x", padx=15, pady=(3, 10))
        tk.Label(row, text="\\network\\SA_Display\\whiteboard.php",
                 bg="white", fg="#123b5d", font=("Consolas", 10, "bold")).pack(side="left")
        tk.Label(row, text="Fixed target", bg="#e8f1f8", fg="#285878",
                 font=("Segoe UI", 8, "bold"), padx=8, pady=3).pack(side="right")

        # Settings card
        settings = tk.Frame(body, bg="white", highlightbackground="#d5dee8", highlightthickness=1)
        settings.pack(fill="x", pady=(0, 10))
        tk.Label(settings, text="ROTATION", bg="white", fg="#5a6b7b",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        srow = tk.Frame(settings, bg="white")
        srow.pack(fill="x", padx=15, pady=(4, 11))
        tk.Label(srow, text="Change image every", bg="white", fg="#233746").pack(side="left")
        spin = ttk.Spinbox(srow, from_=1, to=86400, textvariable=self.seconds_var,
                           width=7, justify="center")
        spin.pack(side="left", padx=8)
        tk.Label(srow, text="seconds", bg="white", fg="#5a6b7b").pack(side="left")

        # Pages card
        pages = tk.Frame(body, bg="white", highlightbackground="#d5dee8", highlightthickness=1)
        pages.pack(fill="x")
        tk.Label(pages, text="DISPLAY PAGES", bg="white", fg="#5a6b7b",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        grid = tk.Frame(pages, bg="white")
        grid.pack(fill="x", padx=12, pady=(0, 10))
        for i, (name, _) in enumerate(URLS):
            r, c = divmod(i, 2)
            cell = tk.Frame(grid, bg="#f7f9fb", highlightbackground="#e0e7ee", highlightthickness=1)
            cell.grid(row=r, column=c, sticky="ew", padx=3, pady=3, ipady=3)
            grid.columnconfigure(c, weight=1)
            ttk.Checkbutton(cell, text=name, variable=self.vars[i]).pack(
                anchor="w", padx=7, pady=3
            )

        controls = tk.Frame(body, bg="#eef3f8")
        controls.pack(fill="x", pady=(12, 0))
        ttk.Button(controls, text="Select All", command=self.select_all).pack(side="left")
        ttk.Button(controls, text="Clear All", command=self.clear_all).pack(side="left", padx=7)
        ttk.Button(controls, text="UPDATE DISPLAY", command=self.update_php).pack(side="right")

        status = tk.Frame(body, bg="#eef3f8")
        status.pack(fill="x", pady=(10, 0))
        tk.Label(status, textvariable=self.status_var, bg="#eef3f8", fg="#5a6b7b",
                 anchor="w", font=("Segoe UI", 8)).pack(fill="x")

    def select_all(self):
        for var in self.vars:
            var.set(True)

    def clear_all(self):
        for var in self.vars:
            var.set(False)

    def update_php(self):
        php_path = Path(self.path_var.get())
        if not php_path.is_file():
            messagebox.showerror(APP_NAME, f"Could not find whiteboard.php at:\\n{php_path}")
            return

        try:
            seconds = int(self.seconds_var.get())
        except ValueError:
            messagebox.showerror(APP_NAME, "Rotation interval must be a whole number.")
            return
        if seconds < 1:
            messagebox.showerror(APP_NAME, "Rotation interval must be at least 1 second.")
            return

        selected = [url for (_, url), var in zip(URLS, self.vars) if var.get()]
        if not selected:
            messagebox.showerror(APP_NAME, "Select at least one display page.")
            return

        try:
            original = php_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            original = php_path.read_text(encoding="cp1252")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not read whiteboard.php:\\n{exc}")
            return

        updated = self._replace_urls(original, selected)
        if updated is None:
            messagebox.showerror(APP_NAME, "whiteboard.php does not match the expected SA display format.")
            return
        updated = self._replace_refresh_interval(updated, seconds)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = php_path.with_name(f"whiteboard.php.bak_{timestamp}")
        try:
            shutil.copy2(php_path, backup)
            php_path.write_text(updated, encoding="utf-8", newline="")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not update whiteboard.php:\\n{exc}")
            return

        self.status_var.set(f"Updated whiteboard.php • {len(selected)} pages • {seconds}s rotation")
        messagebox.showinfo(
            APP_NAME,
            f"Display updated successfully.\\n\\nPages: {len(selected)}\\nRotation: {seconds} seconds\\n\\nBackup created:\\n{backup}"
        )

    @staticmethod
    def _replace_urls(text, urls):
        array_start = text.find("$url = array();")
        if array_start == -1:
            return None
        pattern = re.compile(
            r"(?ms)(\$url\s*=\s*array\(\);\s*)"
            r"(?:\s*\$url\[\d+\]\s*=\s*.*?;)+"
        )
        match = pattern.search(text, array_start)
        if not match:
            return None
        entries = "\\n".join(
            f'    $url[{i}] = "{url}";' for i, url in enumerate(urls)
        )
        replacement = match.group(1) + "\\n" + entries + "\\n"
        return text[:match.start()] + replacement + text[match.end():]

    @staticmethod
    def _replace_refresh_interval(text, seconds):
        return re.sub(
            r'(<META\s+HTTP-EQUIV="refresh"\s*\n?\s*CONTENT=")\d+(;URL=)',
            rf"\g<1>{seconds}\g<2>",
            text,
            flags=re.IGNORECASE,
        )


if __name__ == "__main__":
    DisplayManager().mainloop()
