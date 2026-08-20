# Sani Shwapno Bazar — Inventory Management

A simple inventory tracker built for **Sani Shwapno Bazar**, an online shop selling
Saudi Arabia–sourced products (perfumes, shampoos, dates, etc.) across Bangladesh.

Built with **Django** (Python) + **SQLite** (local) / **PostgreSQL** (hosted).
No frontend framework — plain HTML/CSS, kept intentionally simple.

These instructions assume **Windows, using cmd (Command Prompt), inside VS Code** —
if you're on macOS/Linux or using PowerShell, the commands are slightly different
(noted where it matters).

## What it does

- Track **Companies → Brands → Products** — e.g. Company "L'Oréal" owns Brand
  "L'Oréal Paris"; you set the company once per brand, and every product under
  that brand shows it automatically.
- Each product can have multiple **size/weight variants** — e.g. a shampoo can
  have a "90ml" mini bottle and a "400ml" big bottle, each with its own stock,
  price, and expiry date.
- **Split-batch stock**: the same size can have multiple rows if stock arrived
  in separate batches with different expiry dates (e.g. 3 pieces expiring in
  November, 2 pieces of the same size expiring in August) — each batch is
  tracked and adjusted independently.
- Stock is measured in **pieces, kg, g, litre, or ml** — pieces/box/pack always
  display as whole numbers, weight/volume units keep decimals when relevant.
- **Flexible expiry date entry** — type a full date (`21/08/26`) or just
  month/year if that's all the packaging shows (`08/26`, treated as the last
  day of that month).
- **Stock In / Stock Out** actions update quantity and keep a full movement
  history (so you always know what happened, not just the current number).
  Attempting to remove more stock than exists is rejected with an error.
- **Inventory tab** — all products/variants with filters (company, category,
  brand, country, unit, low-stock, search) and sorting (name, stock, price,
  expiry, date added).
- **Expiry tab** — same data, sorted nearest-expiry-first, with quick range
  filters: All, Expired, Next 7 days, Next 15 days, Next 30 days, Next 3
  months, Next 6 months, Next 1 year.
- **Django Admin** at `/admin/` — the fastest way to bulk-enter your notebook
  data, since you can add a product and all its size/batch variants on one
  screen.

## Project structure

```
inventory-management-ssb/
├── .kiro/steering/        # Notes for AI assistants working on this repo (see below)
├── config/                # Django project settings, urls, wsgi
├── inventory/             # The app: models, views, forms, admin, urls, custom fields
│   └── migrations/
├── templates/inventory/   # HTML templates (base, inventory list, expiry list, forms)
├── static/css/style.css   # All styling (teal theme, Inter font)
├── requirements.txt
├── build.sh               # Used by hosting to install deps + migrate + collectstatic
├── Procfile               # For Render/Heroku-style hosts
└── .env.example           # Template for environment variables
```

## Data model (quick reference)

| Model | Purpose |
|---|---|
| `Company` | Optional parent of a Brand, e.g. "L'Oréal" |
| `Brand` | e.g. Al Rehab, L'Oréal Paris — optionally linked to a Company |
| `Category` | e.g. Shampoo, Perfume, Dates |
| `Product` | The general item — name, brand, category, country of origin, date added |
| `ProductVariant` | The actual stocked unit — size label (e.g. "90ml"), unit, quantity, prices, expiry date, batch number |
| `StockMovement` | Every stock in/out action, logged with date and note |

---

## 1. Cloning the repo (Windows / cmd / VS Code)

1. Open VS Code.
2. Open a terminal: **Terminal → New Terminal** (make sure it's set to
   **Command Prompt**, not PowerShell — check the dropdown in the top-right
   of the terminal panel).
3. Pick a folder to work in and clone the repo:

```cmd
cd C:\Users\YourName\Documents
git clone https://github.com/rafimkl8/inventory-management-ssb.git
cd inventory-management-ssb
```

4. Open the folder in VS Code if it isn't already: **File → Open Folder** →
   select the `inventory-management-ssb` folder you just cloned.

> Don't have Git installed? Download it from
> [git-scm.com/download/win](https://git-scm.com/download/win) and re-open
> your terminal after installing.

## 2. Running it locally

Requires **Python 3.10, 3.11, 3.12, or 3.13** (avoid 3.14 — see
[Troubleshooting](#troubleshooting) below for why).

```cmd
REM Check your Python version first
python --version

REM Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate.bat

REM Your prompt should now start with (venv). Install dependencies:
pip install -r requirements.txt

REM Create the database tables (uses SQLite automatically — a db.sqlite3 file, no install needed)
python manage.py migrate

REM Create your admin login (it will ask for username, email (optional), password)
python manage.py createsuperuser

REM Run the app
python manage.py runserver
```

Then open in your browser:
- **http://127.0.0.1:8000/** — the Inventory tab
- **http://127.0.0.1:8000/expiry/** — the Expiry tab
- **http://127.0.0.1:8000/admin/** — Django Admin (log in with the superuser you created)

Press `Ctrl+C` in the terminal to stop the server when you're done.

That's it — no Postgres, no Docker, nothing else to install locally.

### Coming back to it later

Every time you reopen this project in a new terminal session, re-activate the
virtual environment first:

```cmd
cd C:\Users\YourName\Documents\inventory-management-ssb
venv\Scripts\activate.bat
python manage.py runserver
```

### Getting the latest changes

If updates have been made (e.g. by an AI assistant in another session, or a
teammate), pull them and re-sync your environment:

```cmd
git checkout main
git pull origin main
venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 3. Seeding your notebook data (manual entry, made fast)

Since your data is on paper, the fastest way in is the **Django Admin**:

1. Go to `http://127.0.0.1:8000/admin/` and log in.
2. **One-time setup per brand**: Admin → Companies → Add (only if you want to
   group brands, e.g. "L'Oréal"), then Admin → Brands → Add (pick the Company
   if relevant), then Admin → Categories → Add. Do this once per
   company/brand/category you have — takes a minute, and you won't need to
   repeat it for every product.
3. Go to **Admin → Products → Add product**.
4. Fill in the product name, brand, category, country of origin (defaults to
   "Saudi Arabia"), and date added (defaults to today, but you can backdate
   it for older notebook records).
5. Scroll down — you'll see a **"Product variants"** section right on the
   same page. Add every size **and every batch** of that product as its own
   row:
   - `size_label`: e.g. `90ml`, `400ml`, `500g`, `1kg`
   - `unit` ("Stock counted in"): almost always **Pieces**, even for a
     bottled item like "700ml" — you're counting bottles, not millilitres.
     Only use kg/g/l/ml for genuinely loose/bulk stock sold by weight.
   - `quantity_in_stock`, `reorder_level` (when to warn you it's low)
   - `cost_price`, `selling_price` (in BDT)
   - `expiry_date` — type a full date like `21/08/26`, or just a month/year
     like `08/26` if that's all the packaging shows (treated as the last day
     of that month)
   - **Same size, different expiry?** Add it as a **separate row** — e.g. if
     5 bottles of the same 600ml size arrived with 3 expiring in November and
     2 expiring in August, that's two rows, not one.
6. Click **Save** — done, one product with all its variants in one go.

Repeat per product from your notebook. There's also a lighter
**"+ Add New Product"** button on the Inventory tab itself if you prefer the
simpler custom form (same idea, and it lets you add multiple sizes with the
"+ Add another size" button too).

No CSV import or scripts required — everything above is just typing into a
web form.

### Daily use after seeding
- **Stock In/Out**: open a product (click its name from the Inventory tab),
  and each variant/batch has a small form to add/remove stock with an
  optional note. It's logged automatically so you always have history.
- **Low stock**: check the "Low stock only" filter on the Inventory tab.
- **Expiry check**: use the Expiry tab, sorted nearest-first by default, with
  the quick range filters (Expired, 7/15/30 days, 3/6 months, 1 year).

---

## 4. Hosting it for free (so you can check it from your phone)

Recommended combo: **Render** (free web hosting) + **Neon** (free PostgreSQL).
Neon's free tier has no time limit and is enough for a small personal shop
([Neon free plan details](https://neon.com/faqs/free-plan-limits-and-quotas)).
Render's free tier gives you a live HTTPS URL connected to your GitHub repo
([Render free tier](https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026)).

### Step 1 — Create a free Postgres database on Neon
1. Sign up at [neon.tech](https://neon.tech) (free, no credit card).
2. Create a project — Neon gives you a connection string like:
   `postgresql://user:password@host/dbname?sslmode=require`
3. Copy that connection string — you'll need it as `DATABASE_URL`.

### Step 2 — Deploy to Render
1. Push this repo to GitHub (if not already).
2. Sign up at [render.com](https://render.com) and create a **New Web Service**,
   connecting it to your GitHub repo.
3. Set:
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
4. Add these **Environment Variables** in Render's dashboard:
   ```
   DATABASE_URL = <your Neon connection string>
   SECRET_KEY   = <any long random string>
   DEBUG        = False
   ALLOWED_HOSTS = your-app-name.onrender.com
   CSRF_TRUSTED_ORIGINS = https://your-app-name.onrender.com
   ```
5. Deploy. Render will run `build.sh` (installs deps, runs migrations, collects
   static files) then start the app.
6. Once live, create a superuser for the hosted database. If Render's Shell
   tab is available on your plan, use it to run
   `python manage.py createsuperuser`. Otherwise, temporarily point your local
   `.env` at the same `DATABASE_URL` and run `python manage.py createsuperuser`
   from your machine before deploying.

### Step 3 — Access from your phone
Just open `https://your-app-name.onrender.com/` in your phone's browser — no
app install needed. You can even "Add to Home Screen" for a quick launch icon.

> Note: Render's free web services sleep after inactivity and take ~30-60
> seconds to wake up on the first request. That's normal on the free tier.

---

## Switching between local SQLite and hosted Postgres

You don't need to change any code. The app reads a `DATABASE_URL` environment
variable:
- **Not set** (default, local) → uses SQLite (`db.sqlite3`), zero setup.
- **Set** (e.g. on Render, pointing to Neon) → uses PostgreSQL automatically.

See `.env.example` for the full list of environment variables you can set.

---

## Troubleshooting

### `AttributeError: 'super' object has no attribute 'dicts'` when opening `/admin/...`
This means your Python version is **3.14**, which Django 4.2 (used by this
project) doesn't officially support yet — it's a known Django/Python
incompatibility, not a bug in this app. Fix: create the virtual environment
with an older Python version instead:

```cmd
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

If `python` on your machine points to 3.14 and you have another version
installed too (check with `py -0` or look for `python3.12.exe` etc. on your
system), create the venv explicitly with that version, e.g.:
```cmd
py -3.12 -m venv venv
```
If you don't have an older Python installed, download 3.12 from
[python.org/downloads](https://www.python.org/downloads/) (check "Add
python.exe to PATH" during install), restart your terminal, then retry.

### `'venv' is not recognized` or activation doesn't seem to do anything
Make sure your terminal is **Command Prompt**, not PowerShell (PowerShell
needs `venv\Scripts\Activate.ps1` and may block script execution by default).
Check the terminal type dropdown in VS Code's terminal panel.

### Static files / styling look broken after `collectstatic` or on Render
Make sure `DEBUG=False` is only set when `ALLOWED_HOSTS` and
`CSRF_TRUSTED_ORIGINS` are also correctly set for your domain — see the
hosting section above.

---

## For AI assistants / future sessions

This repo has a `.kiro/steering/project-overview.md` file with the full data
model rationale, coding conventions, and known gotchas (like the Python 3.14
issue above). **Read it before making changes** — it explains *why* things
are built the way they are (e.g. why the same product name can legitimately
appear multiple times in the Inventory tab, why expiry month-only input
rounds to end-of-month, etc.), so you don't accidentally "fix" intentional
behavior. This applies whether you're continuing in the same chat, a new
chat, or a different Kiro account working on this same GitHub repo.

## Tech stack
- Python / Django 4.2
- SQLite (local) or PostgreSQL via `dj-database-url` (hosted)
- Whitenoise for serving static files in production
- Plain HTML/CSS templates — no JS framework, no build step
