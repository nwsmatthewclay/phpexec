@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --windowed --clean --name Sa-Display-Manager sa_display_manager.py
if errorlevel 1 exit /b 1
echo.
echo Built: dist\Sa-Display-Manager.exe
