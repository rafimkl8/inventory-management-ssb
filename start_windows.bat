@echo off
REM ============================================================
REM  Sani Shwapno Bazar - Inventory Launcher (Windows)
REM  Double-click this file. No typing commands required.
REM  First run: sets up everything automatically (slower, one-time).
REM  Later runs: starts instantly.
REM
REM  If anything goes wrong, this window will stay open and show
REM  the error message instead of closing -- read it before you
REM  close the window.
REM ============================================================

setlocal
cd /d "%~dp0"

echo Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ERROR] Python was not found on this computer.
    echo  Install it from https://www.python.org/downloads/
    echo  During install, make sure to check "Add python.exe to PATH".
    echo  Then double-click this file again.
    echo.
    pause
    exit /b 1
)

REM A Windows "Store alias" stub can make `where python` succeed even when
REM no real Python is installed. Actually run it to make sure it works.
python --version >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ERROR] A "python" command exists but doesn't actually run
    echo  ^(this happens with the Windows Store's Python placeholder^).
    echo  Install real Python from https://www.python.org/downloads/
    echo  and make sure "Add python.exe to PATH" is checked.
    echo.
    pause
    exit /b 1
)

REM If a previous run partially failed, the venv folder may exist but be
REM broken (missing python.exe inside it). Treat that the same as "missing".
if exist venv (
    if not exist venv\Scripts\python.exe (
        echo.
        echo  Found a leftover, incomplete "venv" folder from a previous
        echo  attempt -- removing it and starting the one-time setup again.
        echo.
        rmdir /s /q venv
    )
)

if not exist venv (
    echo First time setup - this may take a minute, please wait...
    echo.

    echo Creating the virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to create the virtual environment. See the
        echo  message above for details.
        echo.
        pause
        exit /b 1
    )

    echo Installing dependencies (needs an internet connection)...
    venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
    if errorlevel 1 (
        echo.
        echo  [ERROR] Installing dependencies failed. This usually means
        echo  there was no internet connection during setup.
        echo  Check your connection and double-click this file again.
        echo  ^(It will retry the failed steps -- it won't redo finished ones.^)
        echo.
        pause
        exit /b 1
    )

    echo Setting up the database...
    venv\Scripts\python.exe manage.py migrate
    if errorlevel 1 (
        echo.
        echo  [ERROR] Database setup failed. See the message above.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo Setup complete. If this is a brand new database, create an admin
    echo login now (you'll be asked for a username and password):
    venv\Scripts\python.exe manage.py createsuperuser
) else (
    venv\Scripts\python.exe manage.py migrate
    if errorlevel 1 (
        echo.
        echo  [ERROR] Database setup failed. See the message above.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Starting the server in a new window - KEEP THAT WINDOW OPEN while you use the app.
start "Sani Shwapno Bazar - Server (keep this window open)" cmd /k "cd /d "%~dp0" && venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8000/

echo.
echo The app should now be open in your browser at http://127.0.0.1:8000/
echo If not, open that address manually -- and check the other
echo "Server" window for any error messages.
echo To stop the app later: close the other "Server" window (or press Ctrl+C in it).
echo.
pause
