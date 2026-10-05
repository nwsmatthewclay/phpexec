import re
import shutil
import sys
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
        self.geometry("620x450")
        self.configure(bg="#eef3f8")
        self.option_add("*Font", ("Segoe UI", 10))
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), padding=(14, 7))
        style.configure("TButton", padding=(10, 5))
        style.configure("TCheckbutton", background="#f7f9fb")


        self.php_path = self._get_php_path()
        self.path_var = tk.StringVar(value=str(self.php_path))
        self.seconds_var = tk.StringVar(value=str(DEFAULT_SECONDS))
        self.status_var = tk.StringVar(value="Ready to configure the SA display.")
        self.vars = [tk.BooleanVar(value=i < 5) for i in range(len(URLS))]

        self._build()

    def _build(self):
        self.configure(padx=0, pady=0)

        header = tk.Frame(self, bg="#123b5d", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="SA DISPLAY MANAGER",
            bg="#123b5d", fg="white",
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", padx=22, pady=(14, 0))
        tk.Label(
            header, text="Science & Aviation display rotation",
            bg="#123b5d", fg="#cfe5f5",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=23, pady=(1, 0))

        body = tk.Frame(self, bg="#eef3f8")
        body.pack(fill="both", expand=True, padx=14, pady=14)

        # Rotation
        rotation = tk.Frame(
            body, bg="white",
            highlightbackground="#d5dee8", highlightthickness=1
        )
        rotation.pack(fill="x", pady=(0, 10))

        tk.Label(
            rotation, text="ROTATION",
            bg="white", fg="#5a6b7b",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=14, pady=(9, 2))

        rrow = tk.Frame(rotation, bg="white")
        rrow.pack(anchor="w", padx=14, pady=(0, 10))

        tk.Label(
            rrow, text="Change image every",
            bg="white", fg="#233746"
        ).pack(side="left")

        ttk.Spinbox(
            rrow, from_=1, to=86400,
            textvariable=self.seconds_var,
            width=6, justify="center"
        ).pack(side="left", padx=8)

        tk.Label(
            rrow, text="seconds",
            bg="white", fg="#5a6b7b"
        ).pack(side="left")

        # Pages
        pages = tk.Frame(
            body, bg="white",
            highlightbackground="#d5dee8", highlightthickness=1
        )
        pages.pack(fill="x")

        tk.Label(
            pages, text="DISPLAY PAGES",
            bg="white", fg="#5a6b7b",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=14, pady=(9, 5))

        grid = tk.Frame(pages, bg="white")
        grid.pack(fill="x", padx=11, pady=(0, 11))

        for i, (name, _) in enumerate(URLS):
            row, col = divmod(i, 2)
            cell = tk.Frame(
                grid, bg="#f7f9fb",
                highlightbackground="#e0e7ee", highlightthickness=1
            )
            cell.grid(row=row, column=col, sticky="ew", padx=3, pady=3, ipady=2)
            grid.columnconfigure(col, weight=1)

            tk.Checkbutton(
                cell, text=name, variable=self.vars[i],
                bg="#f7f9fb", activebackground="#f7f9fb",
                selectcolor="white", anchor="w",
                font=("Segoe UI", 9)
            ).pack(fill="x", padx=5, pady=2)

        # Action buttons -- use native Tk buttons so labels always render.
        actions = tk.Frame(body, bg="#eef3f8")
        actions.pack(fill="x", pady=(12, 0))

        tk.Button(
            actions, text="Select All",
            command=self.select_all,
            font=("Segoe UI", 9),
            padx=10, pady=4
        ).pack(side="left")

        tk.Button(
            actions, text="Clear All",
            command=self.clear_all,
            font=("Segoe UI", 9),
            padx=10, pady=4
        ).pack(side="left", padx=7)

        tk.Button(
            actions, text="UPDATE DISPLAY",
            command=self.update_php,
            bg="#123b5d", fg="white",
            activebackground="#1d527c", activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            padx=14, pady=5
        ).pack(side="right")

        tk.Label(
            body, textvariable=self.status_var,
            bg="#eef3f8", fg="#5a6b7b",
            anchor="w", font=("Segoe UI", 8)
        ).pack(fill="x", pady=(8, 0))

    @staticmethod
    def _get_php_path():
        # In the compiled EXE, always use the folder containing the EXE.
        # This preserves the original workflow: EXE and whiteboard.php live together.
        base = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
        return base / "whiteboard.php"

    def select_all(self):
        for var in self.vars:
            var.set(True)

    def clear_all(self):
        for var in self.vars:
            var.set(False)

    def update_php(self):
        php_path = self.php_path
        if not php_path.is_file():
            messagebox.showerror(
                APP_NAME,
                f"Could not find whiteboard.php in the same folder as the EXE.\n\n{php_path}"
            )
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

        # Recreate the entire PHP file from a known-good template rather than
        # trying to modify whatever formatting happens to be in the existing file.
        php = self._build_php(selected, seconds)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = php_path.with_name(f"whiteboard.php.bak_{timestamp}")

        try:
            shutil.copy2(php_path, backup)
            php_path.write_text(php, encoding="utf-8", newline="")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not update whiteboard.php:\n{exc}")
            return

        self.status_var.set(
            f"Updated whiteboard.php • {len(selected)} pages • {seconds}s rotation"
        )
        messagebox.showinfo(
            APP_NAME,
            f"Display updated successfully.\n\n"
            f"Pages: {len(selected)}\n"
            f"Rotation: {seconds} seconds\n\n"
            f"Backup created:\n{backup}"
        )

    @staticmethod
    def _build_php(urls, seconds):
        # This is the complete whiteboard.php template. The URL entries are
        # deliberately joined with real newline characters so each assignment
        # occupies its own physical line in the PHP file.
        url_lines = "\n".join(
            f'    $url[{i}] = "{url}";' for i, url in enumerate(urls)
        )

        return f'''<html>

<head>

    <?php

    $url = array();

{url_lines}


    foreach (glob("/home/samba/html/SA_Display/*.png") as $filename) {{
        $fileModTime = filemtime($filename);
        $currentTime = time();
        $secondsInDay = 86400;

        if (($currentTime - $fileModTime) < $secondsInDay) {{
             $url[] = "http://198.206.38.246/SA_Display/" . basename($filename);
        }}
    }}

    if (isset($_GET['slide'])) {{
        $slide = $_GET['slide'];
    }} else {{
        $slide = '0';
    }}
    if ($slide > count($url) - 1) {{
        $slide = '0';
    }}
    ?>
    <META HTTP-EQUIV="refresh"
        CONTENT="{seconds};URL=http://198.206.38.246/SA_Display/whiteboard.php?slide=<?php echo $slide + 1; ?>">
    <style type="text/css">
        body {{
            margin: 0;
            height: 100%;
            overflow: hidden;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            frameborder: 0;
            scrolling: no;
            -webkit-transform-origin: 0 0;
        }}

        img {{
            height: 100%;
            max-width: 100%;
        }}
    </style>
</head>

<body>

    <?php
    $img_extensions = array('jpg', 'png', 'gif');
    if (in_array(substr($url[$slide], -3, strlen($url[$slide])), $img_extensions)) {{
        echo '<center><img src="' . $url[$slide] . '?' . rand(1,1000000) . '"></img></center>';
    }} else {{
        echo '<iframe src="' . $url[$slide] . '?' . rand(1,1000000) . '"></iframe>';
    }}

    ?>

    <script>
        var loaded = false;
        var time = 60000;
        window.onload = function () {{
            loaded = true;
        }};
        setTimeout(function () {{
            if (!loaded) {{
                window.location = "http://198.206.38.246/SA_Display/whiteboard.php?slide=<?php echo $slide + 1; ?>";
            }}
        }}, time);
    </script>

</body>

</html>
'''

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
        entries = "\n".join(
            f'    $url[{i}] = "{url}";' for i, url in enumerate(urls)
        )
        replacement = match.group(1) + "\n" + entries + "\n"
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
