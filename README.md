# Sani Shwapno Bazar — Inventory Management

A simple inventory tracker built for **Sani Shwapno Bazar**, an online shop selling
Saudi Arabia–sourced products (perfumes, shampoos, dates, etc.) across Bangladesh.

Built with **Django** (Python) + **SQLite** (local) / **PostgreSQL** (hosted).
No frontend framework — plain HTML/CSS, kept intentionally simple.

## What it does

- Track **Products** grouped by **Brand**, **Category**, and **country of origin**.
- Each product can have multiple **variants** — e.g. a shampoo can have a "90ml"
  mini bottle and a "400ml" big bottle, each with its own stock, price, and expiry.
- Stock is measured in **pieces, kg, g, litre, or ml** — whatever fits the item.
- **Stock In / Stock Out** actions update quantity and keep a full movement history
  (so you always know what happened, not just the current number).
- **Inventory tab** — all products/variants with filters (category, brand, country,
  unit, low-stock) and sorting (name, stock, price, expiry).
- **Expiry tab** — same data, always sorted nearest-expiry-first, with quick chips
  for Expired / Next 7 days / Next 30 days / Next 90 days.
- **Django Admin** at `/admin/` — the fastest way to bulk-enter your notebook data,
  since you can add a product and all its size variants on one screen.

## Project structure

```
inventory-management-ssb/
├── config/            # Django project settings, urls, wsgi
├── inventory/         # The app: models, views, forms, admin, urls
│   └── migrations/
├── templates/inventory/  # HTML templates (base, inventory list, expiry list, forms)
├── static/css/style.css  # All styling
├── requirements.txt
├── build.sh           # Used by hosting to install deps + migrate + collectstatic
├── Procfile           # For Render/Heroku-style hosts
└── .env.example        # Template for environment variables
```

## Data model (quick reference)

| Model | Purpose |
|---|---|
| `Category` | e.g. Shampoo, Perfume, Dates |
| `Brand` | e.g. Al Rehab, Head & Shoulders |
| `Product` | The general item — name, brand, category, country of origin |
| `ProductVariant` | The actual stocked unit — size label (e.g. "90ml"), unit, quantity, prices, expiry date, batch number |
| `StockMovement` | Every stock in/out action, logged with date and note |

---

## 1. Running it locally (no setup needed beyond Python)

Requires Python 3.10+ (already true for most modern machines).

```bash
cd inventory-management-ssb

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create the database tables (uses SQLite automatically — a db.sqlite3 file, no install needed)
python manage.py migrate

# Create your admin login
python manage.py createsuperuser
# it will ask for a username, email (optional), and password

# Run the app
python manage.py runserver
```

Then open in your browser:
- **http://127.0.0.1:8000/** — the Inventory tab
- **http://127.0.0.1:8000/expiry/** — the Expiry tab
- **http://127.0.0.1:8000/admin/** — Django Admin (log in with the superuser you created)

That's it — no Postgres, no Docker, nothing else to install locally.

---

## 2. Seeding your notebook data (manual entry, made fast)

Since your data is on paper, the fastest way in is the **Django Admin**:

1. Go to `http://127.0.0.1:8000/admin/` and log in.
2. First, quickly add your **Brands** and **Categories** (Admin → Brands → Add, Admin → Categories → Add). Do this once for each brand/category you have — takes a minute.
3. Go to **Admin → Products → Add product**.
4. Fill in the product name, brand, category, and country of origin (defaults to "Saudi Arabia").
5. Scroll down — you'll see a **"Product variants"** section right on the same page.
   This is where you add every size/weight of that product as its own row:
   - `size_label`: e.g. `90ml`, `400ml`, `500g`, `1kg`, `1pc`
   - `unit`: pcs / kg / g / l / ml / box / pack
   - `quantity_in_stock`, `reorder_level` (when to warn you it's low)
   - `cost_price`, `selling_price` (in BDT)
   - `expiry_date` (leave blank if not applicable)
6. Click **Save** — done, one product with all its variants in one go.

Repeat per product from your notebook. There's also a lighter **"+ Add New Product"**
button on the Inventory tab itself if you prefer the simpler custom form (same idea,
fewer admin-only fields visible).

No CSV import or scripts required — everything above is just typing into a web form.

### Daily use after seeding
- **Stock In/Out**: open a product (click its name from the Inventory tab), and each
  variant has a small form to add/remove stock with an optional note. It's logged
  automatically so you always have history.
- **Low stock**: check the "Low stock only" filter on the Inventory tab.
- **Expiry check**: use the Expiry tab, sorted nearest-first by default, with the
  quick date-range chips.

---

## 3. Hosting it for free (so you can check it from your phone)

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
6. Once live, visit `https://your-app-name.onrender.com/admin/` and create a
   superuser. Since Render's free web shell may not be available on the free
   tier, you can instead set a one-off environment-based superuser locally
   against the same `DATABASE_URL` before deploying, or use Render's "Shell"
   tab if included in your plan to run:
   ```bash
   python manage.py createsuperuser
   ```

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

## Tech stack
- Python / Django 4.2
- SQLite (local) or PostgreSQL via `dj-database-url` (hosted)
- Whitenoise for serving static files in production
- Plain HTML/CSS templates — no JS framework, no build step
