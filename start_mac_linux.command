#!/usr/bin/env bash
# ============================================================
#  Sani Shwapno Bazar - Inventory Launcher (macOS / Linux)
#  Double-click this file (macOS: you may need to right-click ->
#  Open the first time, since it's from the internet).
#  First run: sets up everything automatically (slower, one-time).
#  Later runs: starts instantly.
# ============================================================

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo "Python was not found on this computer."
    echo "Please install Python 3.10-3.13 from https://www.python.org/downloads/"
    echo
    read -p "Press Enter to close..." _
    exit 1
fi

if [ ! -d venv ]; then
    echo "First time setup - this may take a minute, please wait..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    echo
    echo "Setup complete. If this is a brand new database, create an admin"
    echo "login now (you'll be asked for a username and password):"
    python manage.py createsuperuser
else
    source venv/bin/activate
    python manage.py migrate
fi

echo
echo "Starting the server... KEEP THIS WINDOW OPEN while you use the app."
echo "To stop the app later: come back to this window and press Ctrl+C."
echo

# Open the browser shortly after the server starts.
( sleep 2
  if command -v open >/dev/null 2>&1; then
      open "http://127.0.0.1:8000/"        # macOS
  elif command -v xdg-open >/dev/null 2>&1; then
      xdg-open "http://127.0.0.1:8000/"    # Linux
  fi
) &

python manage.py runserver 127.0.0.1:8000
