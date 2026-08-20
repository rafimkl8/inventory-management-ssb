from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ProductForm, ProductVariantForm, StockMovementForm
from .models import Brand, Category, Product, ProductVariant, StockMovement

VariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True,
)


def _apply_common_filters(qs, request):
    """Apply category/brand/country/unit/search filters shared by list views."""
    category = request.GET.get("category")
    brand = request.GET.get("brand")
    country = request.GET.get("country")
    unit = request.GET.get("unit")
    search = request.GET.get("q")
    low_stock = request.GET.get("low_stock")

    if category:
        qs = qs.filter(product__category_id=category)
    if brand:
        qs = qs.filter(product__brand_id=brand)
    if country:
        qs = qs.filter(product__country_of_origin=country)
    if unit:
        qs = qs.filter(unit=unit)
    if search:
        qs = qs.filter(product__name__icontains=search)
    if low_stock:
        qs = qs.filter(quantity_in_stock__lte=F("reorder_level"))
    return qs


def _filter_context(request):
    return {
        "categories": Category.objects.all(),
        "brands": Brand.objects.all(),
        "countries": Product.objects.order_by().values_list(
            "country_of_origin", flat=True
        ).distinct(),
        "units": ProductVariant.UNIT_CHOICES,
        "selected": {
            "category": request.GET.get("category", ""),
            "brand": request.GET.get("brand", ""),
            "country": request.GET.get("country", ""),
            "unit": request.GET.get("unit", ""),
            "q": request.GET.get("q", ""),
            "low_stock": request.GET.get("low_stock", ""),
            "sort": request.GET.get("sort", ""),
        },
    }


SORT_MAP = {
    "name": "product__name",
    "-name": "-product__name",
    "stock": "quantity_in_stock",
    "-stock": "-quantity_in_stock",
    "price": "selling_price",
    "-price": "-selling_price",
    "expiry": "expiry_date",
    "-expiry": "-expiry_date",
    "added": "product__date_added",
    "-added": "-product__date_added",
}


def inventory_list(request):
    """Main tab: all variants, with filters and sort."""
    qs = ProductVariant.objects.select_related("product", "product__brand", "product__category")
    qs = _apply_common_filters(qs, request)

    sort = request.GET.get("sort", "name")
    order = SORT_MAP.get(sort, "product__name")
    qs = qs.order_by(order)

    context = _filter_context(request)
    context["variants"] = qs
    context["active_tab"] = "inventory"
    return render(request, "inventory/inventory_list.html", context)


def expiry_list(request):
    """Expiry tab: variants that have an expiry date, nearest expiry first.

    Supports a quick range filter: expired / 7 / 30 / 90 / all.
    """
    qs = ProductVariant.objects.select_related("product", "product__brand", "product__category")
    qs = qs.filter(expiry_date__isnull=False)
    qs = _apply_common_filters(qs, request)

    today = timezone.localdate()
    range_filter = request.GET.get("range", "")
    if range_filter == "expired":
        qs = qs.filter(expiry_date__lt=today)
    elif range_filter in {"7", "30", "90"}:
        days = int(range_filter)
        qs = qs.filter(expiry_date__gte=today, expiry_date__lte=today + timedelta(days=days))

    sort = request.GET.get("sort", "expiry")
    order = SORT_MAP.get(sort, "expiry_date")
    qs = qs.order_by(order)

    context = _filter_context(request)
    context["variants"] = qs
    context["active_tab"] = "expiry"
    context["range_filter"] = range_filter
    return render(request, "inventory/expiry_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    variants = product.variants.all()
    return render(
        request,
        "inventory/product_detail.html",
        {"product": product, "variants": variants},
    )


def product_add(request):
    """Add a new product, with all its size/weight variants in one form."""
    if request.method == "POST":
        form = ProductForm(request.POST)
        formset = VariantFormSet(request.POST, instance=Product())
        if form.is_valid():
            product = form.save(commit=False)
            formset = VariantFormSet(request.POST, instance=product)
            if formset.is_valid():
                product.save()
                formset.instance = product
                formset.save()
                messages.success(request, f"Product '{product.name}' added successfully.")
                return redirect("inventory:product_detail", pk=product.pk)
    else:
        form = ProductForm()
        formset = VariantFormSet(instance=Product())

    return render(
        request,
        "inventory/product_form.html",
        {"form": form, "formset": formset, "is_edit": False},
    )


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        formset = VariantFormSet(request.POST, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Product '{product.name}' updated.")
            return redirect("inventory:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)
        formset = VariantFormSet(instance=product)

    return render(
        request,
        "inventory/product_form.html",
        {"form": form, "formset": formset, "is_edit": True, "product": product},
    )


def stock_action(request, pk):
    """Handle a stock IN or OUT action for a single variant."""
    variant = get_object_or_404(ProductVariant, pk=pk)
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.variant = variant
            if movement.movement_type == "in":
                variant.quantity_in_stock += movement.quantity
            else:
                if movement.quantity > variant.quantity_in_stock:
                    messages.error(request, "Not enough stock for this OUT movement.")
                    return redirect("inventory:product_detail", pk=variant.product_id)
                variant.quantity_in_stock -= movement.quantity
            variant.save()
            movement.save()
            messages.success(
                request,
                f"{movement.get_movement_type_display()} of {movement.quantity} recorded for {variant}.",
            )
    return redirect("inventory:product_detail", pk=variant.product_id)
