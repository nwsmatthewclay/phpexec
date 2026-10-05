# SA Display Manager

Windows utility for configuring the NWS SA display by editing the server's `whiteboard.php`.

## Features
- Choose the network/shared `whiteboard.php`.
- Set the rotation interval in seconds.
- Select any combination of six SA Dashboard pages.
- Automatically back up `whiteboard.php` before editing.
- Preserve the rest of the PHP file.
- Build a standalone Windows executable named `Sa-Display-Manager.exe`.

## Pages
1. Main Dashboard
2. Calendar
3. Recreation
4. Mountain
5. Products
6. Verification

## Build
Run `build.bat` on Windows with Python installed.

GitHub Actions also builds the executable on every push to `main` and publishes it as the `Sa-Display-Manager` workflow artifact.
