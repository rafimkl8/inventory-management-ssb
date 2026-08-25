# Build Guide — Sani Shwapno Bazar E-Commerce (Tier A)

**For:** you (the developer), building this solo with AI assistance
**Stack:** Django REST Framework (backend API) + React/Vite (frontend SPA) + PostgreSQL (Supabase or Neon) + Cloudinary (images) + Fly.io or Railway (backend hosting) + Vercel, Netlify, or Cloudflare Pages (frontend hosting)

This stack was chosen specifically because it uses your actual learning stack (Python, Django, React) end-to-end, while still hitting the speed targets discussed (no server "sleep" delays, CDN-served frontend, optimized images).

---

## 0. Before You Start — Decisions to Lock In

- **Keep the existing `inventory-management-ssb` app private**, exactly as-is, for the shop owner's stock/expiry/batch tracking. Don't merge it into the new project — the new storefront is a separate system that reads/writes its own `Order` data, and can optionally query the same product data if you connect them to the same database (see Section 1.1).
- **Repo structure:** a single monorepo is easiest to manage solo:

```
sani-shwapno-bazar/
├── backend/                 # Django + DRF project (the API)
│   ├── config/              # settings, urls, wsgi/asgi
│   ├── inventory/           # Company, Brand, Category, Product, ProductVariant, StockMovement
│   ├── storefront/          # NEW app: Order, OrderItem, public API views
│   ├── manage.py
│   └── requirements.txt
├── frontend/                # React (Vite) single-page app
│   ├── src/
│   │   ├── api/             # fetch/axios wrapper functions
│   │   ├── components/      # ProductCard, CartItem, Navbar, etc.
│   │   ├── pages/           # Home, Category, ProductDetail, Cart, Checkout, Confirmation
│   │   ├── context/         # CartContext (cart state + localStorage)
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

### 0.1 One database or two?
Simplest path: **one Postgres database, two Django apps inside the same project** — `inventory` (your existing models, kept private/admin-only) and `storefront` (new: `Order`, `OrderItem`). This way product/stock data is always in sync automatically — no duplication, no sync jobs needed.

---

## 1. Backend: Django REST Framework Setup

### 1.1 Install
```bash
pip install djangorestframework django-cors-headers dj-database-url django-cloudinary-storage cloudinary
```

### 1.2 `settings.py` additions
```python
INSTALLED_APPS = [
    # ...existing apps...
    "rest_framework",
    "corsheaders",
    "cloudinary_storage",
    "cloudinary",
    "storefront",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",   # must be high up, before CommonMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...rest unchanged...
]

CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "http://localhost:5173",  # Vite dev server, for local development
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
}
```
`AllowAny` is the default because product browsing must be public — you'll explicitly lock down specific views that shouldn't be (Section 6).

### 1.3 New `storefront` app — models
```python
# storefront/models.py
from decimal import Decimal
from django.db import models
from inventory.models import ProductVariant

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid (COD)"),
        ("advance_pending", "Advance Reported - Awaiting Verification"),
        ("advance_confirmed", "Advance Verified"),
        ("full_pending", "Full Payment Reported - Awaiting Verification"),
        ("full_confirmed", "Full Payment Verified"),
    ]

    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default="cod")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    transaction_id = models.CharField(max_length=50, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_required = models.BooleanField(default=False)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price
```

### 1.4 Delivery/advance charge logic — pure function, reusable and testable
```python
# storefront/services.py
from decimal import Decimal

def calculate_delivery_terms(subtotal: Decimal) -> dict:
    """Returns whether an advance is required and how much, based on order subtotal.

    NOTE: confirm exact thresholds with the client before hardcoding —
    current assumption: >5000 -> 200tk advance, >3000 -> 130tk advance, else none.
    """
    if subtotal > Decimal("5000"):
        return {"advance_required": True, "advance_amount": Decimal("200")}
    if subtotal > Decimal("3000"):
        return {"advance_required": True, "advance_amount": Decimal("130")}
    return {"advance_required": False, "advance_amount": Decimal("0")}
```
**Important:** always call this function **server-side** when an order is created — never trust an advance amount sent from the frontend. The frontend can show it for UX purposes, but the backend recalculates from the actual cart contents to prevent tampering.

### 1.5 Serializers
```python
# storefront/serializers.py
from rest_framework import serializers
from inventory.models import Product, ProductVariant, Category
from .models import Order, OrderItem

class ProductVariantPublicSerializer(serializers.ModelSerializer):
    """Public-safe fields only — no cost_price, batch_number, or exact stock counts."""
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ["id", "size_label", "selling_price", "in_stock"]

    def get_in_stock(self, obj):
        return obj.quantity_in_stock > 0


class ProductPublicSerializer(serializers.ModelSerializer):
    variants = ProductVariantPublicSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "brand", "variants"]
        # add "image_url" here once the field exists (Section 3)


class OrderItemInputSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
    transaction_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    items = OrderItemInputSerializer(many=True)
```

### 1.6 Views
```python
# storefront/views.py
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from inventory.models import Product, ProductVariant, Category
from .models import Order, OrderItem
from .serializers import ProductPublicSerializer, OrderCreateSerializer
from .services import calculate_delivery_terms


class ProductListView(generics.ListAPIView):
    serializer_class = ProductPublicSerializer

    def get_queryset(self):
        qs = Product.objects.prefetch_related("variants").select_related("category", "brand")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__id=category)
        return qs


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related("variants").select_related("category", "brand")
    serializer_class = ProductPublicSerializer


class OrderCreateView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        subtotal = Decimal("0")
        line_items = []
        for item in data["items"]:
            variant = get_object_or_404(ProductVariant, pk=item["variant_id"])
            if item["quantity"] > variant.quantity_in_stock:
                return Response({"error": f"Not enough stock for {variant}"}, status=400)
            line_total = variant.selling_price * item["quantity"]
            subtotal += line_total
            line_items.append((variant, item["quantity"], variant.selling_price))

        terms = calculate_delivery_terms(subtotal)

        order = Order.objects.create(
            customer_name=data["customer_name"],
            phone=data["phone"],
            address=data["address"],
            payment_method=data["payment_method"],
            transaction_id=data.get("transaction_id", ""),
            subtotal=subtotal,
            advance_required=terms["advance_required"],
            advance_amount=terms["advance_amount"],
            payment_status="advance_pending" if data["payment_method"] != "cod" else "unpaid",
        )
        for variant, qty, price in line_items:
            OrderItem.objects.create(order=order, variant=variant, quantity=qty, unit_price=price)

        return Response({
            "order_id": order.pk,
            "subtotal": subtotal,
            "advance_required": terms["advance_required"],
            "advance_amount": terms["advance_amount"],
        }, status=status.HTTP_201_CREATED)
```

### 1.7 URLs
```python
# storefront/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("orders/", views.OrderCreateView.as_view(), name="order-create"),
]
```

### 1.8 Admin — manual payment confirmation workflow
```python
# storefront/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_name", "phone", "payment_method", "payment_status", "subtotal", "is_confirmed", "created_at"]
    list_filter = ["payment_method", "payment_status", "is_confirmed"]
    inlines = [OrderItemInline]
    actions = ["mark_confirmed"]

    def mark_confirmed(self, request, queryset):
        queryset.update(is_confirmed=True)
    mark_confirmed.short_description = "Mark selected orders as payment-confirmed"
```
This is where the shop owner does the manual bKash/Nagad transaction check — after confirming a `transaction_id` matches a real payment in their bKash/Nagad app, they select the order(s) and run this action.

---

## 2. Wire It Up
```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inventory.urls")),       # existing private inventory pages
    path("api/", include("storefront.urls")),  # new public API
]
```

---

## 3. Image Handling (Cloudinary)

**Recommended shortcut for v1 (avoids backend upload complexity):**
1. Sign up for Cloudinary's free tier.
2. Shop owner uploads product photos directly through Cloudinary's web console.
3. Copy the resulting image URL, paste it into a new `image_url` field you add to `Product` in `inventory/models.py`:
```python
image_url = models.URLField(blank=True, help_text="Paste the Cloudinary image URL here.")
```
4. Add `f_auto,q_auto` to the Cloudinary URL (auto format + auto quality) for automatic compression — Cloudinary supports this via URL transformation parameters, no extra code needed.

This gets you shipping fast without building a file-upload endpoint. You can automate direct in-admin uploads later as a v2 improvement.

---

## 4. Frontend: React (Vite) Setup

### 4.1 Scaffold
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install axios react-router-dom @tanstack/react-query
```
`@tanstack/react-query` caches API responses (e.g. the product list) so navigating between pages feels instant instead of refetching every time — directly helps the "superfast" goal.

### 4.2 Pages to build
- `Home.jsx` — featured categories/products
- `CategoryPage.jsx` — paginated product grid, filterable
- `ProductDetailPage.jsx` — variant/size selector, add to cart
- `CartPage.jsx` — review/update quantities
- `CheckoutPage.jsx` — customer info form + payment method + dynamic advance-charge display
- `OrderConfirmationPage.jsx` — order summary + WhatsApp link button

### 4.3 Cart — keep it client-side, no backend calls until checkout
```jsx
// src/context/CartContext.jsx
import { createContext, useContext, useEffect, useState } from "react";

const CartContext = createContext();

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => JSON.parse(localStorage.getItem("cart") || "[]"));

  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(items));
  }, [items]);

  const addItem = (variantId, name, price, quantity = 1) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.variantId === variantId);
      if (existing) {
        return prev.map((i) => i.variantId === variantId ? { ...i, quantity: i.quantity + quantity } : i);
      }
      return [...prev, { variantId, name, price, quantity }];
    });
  };

  const subtotal = items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  return (
    <CartContext.Provider value={{ items, addItem, subtotal, setItems }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
```
Storing cart in `localStorage` means it survives a page refresh — important since customers will likely browse, leave, come back later.

### 4.4 Checkout — mirror the delivery-charge logic for instant UI feedback
```jsx
function calculateDeliveryTerms(subtotal) {
  if (subtotal > 5000) return { advanceRequired: true, advanceAmount: 200 };
  if (subtotal > 3000) return { advanceRequired: true, advanceAmount: 130 };
  return { advanceRequired: false, advanceAmount: 0 };
}
```
Show this instantly in the UI as the cart total changes — but remember, the **backend recalculates this independently** on order submission (Section 1.4), so a tampered frontend value can never actually change what gets charged/confirmed.

### 4.5 On order submit
```jsx
const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/orders/`, {
  customer_name, phone, address, payment_method, transaction_id,
  items: cartItems.map(i => ({ variant_id: i.variantId, quantity: i.quantity })),
});
// res.data has the server-confirmed subtotal/advance_amount — use THIS to build the WhatsApp message and confirmation page, not the client-side estimate.
```

### 4.6 WhatsApp deep link
```jsx
function buildWhatsAppLink(order, items) {
  const lines = [
    `New order from ${order.customer_name} (${order.phone})`,
    ...items.map(i => `- ${i.name} x${i.quantity}`),
    `Subtotal: ${order.subtotal} BDT`,
    order.advance_required ? `Advance required: ${order.advance_amount} BDT` : "COD - no advance",
    `Address: ${order.address}`,
  ];
  const text = encodeURIComponent(lines.join("\n"));
  return `https://wa.me/8801XXXXXXXXX?text=${text}`;
}
```

### 4.7 Environment variables
```
# frontend/.env
VITE_API_BASE_URL=https://api.sanishwapnobazar.com
```

---

## 5. Security Checklist

- [ ] Public API (`/api/products/`) exposes **only** public-safe fields — never `cost_price`, `batch_number`, or exact stock counts (show `in_stock: true/false` instead of raw numbers, as in the serializer above).
- [ ] `OrderCreateView` **recalculates** subtotal and delivery/advance charge server-side from actual product prices — never trusts a total sent from the frontend.
- [ ] `CORS_ALLOWED_ORIGINS` set to your actual frontend domain only — never `"*"` in production.
- [ ] Existing private inventory views (`product_add`, `product_edit`, `stock_action` in `inventory/views.py`) get `@login_required` added before this goes live publicly — currently unprotected.
- [ ] `DEBUG = False` in production, with `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` set correctly for both frontend and backend domains.
- [ ] HTTPS enforced on both frontend and backend (automatic via chosen hosts, just verify the padlock after deploy).
- [ ] Basic validation on order creation (required fields, phone format) to reduce spam/fake orders.

---

## 6. Performance Checklist

- [ ] Frontend deployed as a static build to Vercel/Netlify/Cloudflare Pages — served from CDN, no cold start.
- [ ] Backend deployed on Fly.io or Railway (not a free tier that sleeps) — pick a region close to Bangladesh if available (Fly.io has a Singapore region).
- [ ] Cloudinary image URLs include `f_auto,q_auto` for automatic compression/format.
- [ ] `loading="lazy"` on all product images below the fold.
- [ ] API responses paginated (`PAGE_SIZE = 24` set above) — never return the full catalog in one response.
- [ ] React Query caching enabled so repeat navigation doesn't refetch unnecessarily.
- [ ] `select_related`/`prefetch_related` used on every queryset touching related models (already applied in `ProductListView` above) — same discipline your existing `inventory/views.py` already follows, keep it consistent here.

---

## 7. Testing Checklist Before Launch

- [ ] Place a real test order for each payment method: COD, bKash advance, Nagad advance, full advance.
- [ ] Test order **below ৳3,000** → confirm no advance is requested.
- [ ] Test order **between ৳3,000–5,000** → confirm ৳130 advance is requested.
- [ ] Test order **above ৳5,000** → confirm ৳200 advance is requested.
- [ ] Confirm each test order appears correctly in Django Admin, and the "mark confirmed" action works.
- [ ] Test on an actual phone over mobile data (not just wifi/laptop) — this is the real usage condition for Facebook shop customers.
- [ ] Confirm stock doesn't oversell (try ordering more than available quantity — should be rejected, per `OrderCreateView` above).
- [ ] Confirm the WhatsApp link opens correctly with the pre-filled message on both Android and iOS.

---

## 8. Deployment Steps

1. **Database:** create a Postgres project on Supabase or Neon, copy the connection string.
2. **Backend (Fly.io or Railway):** connect the `backend/` folder, set environment variables (`SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, Cloudinary keys if used), deploy, run migrations, create a superuser.
3. **Frontend (Vercel/Netlify/Cloudflare Pages):** connect the `frontend/` folder, set `VITE_API_BASE_URL` to the deployed backend URL, deploy.
4. **Domain:** point the root domain (e.g. `sanishwapnobazar.com`) to the frontend host, and a subdomain (e.g. `api.sanishwapnobazar.com`) to the backend host. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` to match the final domains.
5. **SSL:** automatic via both hosts — verify the padlock shows on both domains after DNS propagates.

---

## 9. Post-Launch

- Set up free uptime monitoring (e.g. UptimeRobot) to alert you if the backend goes down.
- Check Django Admin regularly for orders stuck in `advance_pending`/`full_pending` that need manual verification.
- Periodically back up the database (export via `pg_dump` if on a free tier without automated backups).

---

## 10. Suggested Milestone Timeline (solo, AI-assisted)

| Week | Focus |
|---|---|
| 1 | Backend: models, API endpoints, admin, delivery-charge logic |
| 2 | Frontend: product pages, cart |
| 3 | Checkout flow, COD/bKash/Nagad/advance logic, WhatsApp notification |
| 4 | Responsive styling pass, image optimization, full testing |
| 5 (buffer) | Deployment, domain setup, bug fixes |

This lines up with the 3–5 week Tier A timeline quoted to the client.
