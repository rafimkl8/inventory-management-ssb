@echo off
REM ============================================================
REM  Sani Shwapno Bazar - Inventory Launcher (Windows)
REM  Double-click this file. No typing commands required.
REM  First run: sets up everything automatically (slower, one-time).
REM  Later runs: starts instantly.
REM ============================================================

setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  Python was not found on this computer.
    echo  Please install Python 3.10-3.13 from https://www.python.org/downloads/
    echo  During install, make sure to check "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

if not exist venv (
    echo First time setup - this may take a minute, please wait...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    python manage.py migrate
    echo.
    echo Setup complete. If this is a brand new database, create an admin
    echo login now (you'll be asked for a username and password):
    python manage.py createsuperuser
) else (
    call venv\Scripts\activate.bat
    python manage.py migrate
)

echo.
echo Starting the server in a new window - KEEP THAT WINDOW OPEN while you use the app.
start "Sani Shwapno Bazar - Server (keep this window open)" cmd /k "venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8000/

echo.
echo The app should now be open in your browser at http://127.0.0.1:8000/
echo If not, open that address manually.
echo To stop the app later: close the other "Server" window (or press Ctrl+C in it).
echo.
pause
