from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Product category, e.g. Shampoo, Perfume, Dates."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Brand of a product, e.g. Al Rehab, Sadia."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """A general product, e.g. 'Al Rehab Musk Perfume'.

    Actual stock is tracked per ProductVariant (e.g. different sizes),
    not on the Product itself.
    """

    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    country_of_origin = models.CharField(
        max_length=100,
        default="Saudi Arabia",
        help_text="Country the product is imported/sourced from.",
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.brand})"

    def get_absolute_url(self):
        return reverse("inventory:product_detail", args=[self.pk])


class ProductVariant(models.Model):
    """A specific stocked/sellable unit of a Product.

    Example: 'Head & Shoulders' Product might have two variants:
    '90ml' and '400ml', each with its own stock, price, and expiry.
    """

    UNIT_CHOICES = [
        ("pcs", "Pieces"),
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Litre"),
        ("ml", "Millilitre"),
        ("box", "Box"),
        ("pack", "Pack"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size_label = models.CharField(
        max_length=50,
        help_text="e.g. '90ml', '400ml', '500g', '1kg', '1pc'",
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="pcs")
    sku = models.CharField(max_length=50, blank=True, help_text="Optional internal code.")
    quantity_in_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Alert when stock falls at/below this level.",
    )
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost per unit (BDT).")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Selling price per unit (BDT).")
    batch_number = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product__name", "size_label"]

    def __str__(self):
        return f"{self.product.name} - {self.size_label}"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    @property
    def expiry_status(self):
        """Returns one of: 'expired', 'critical' (<=30d), 'warning' (<=90d), 'ok', or None."""
        if not self.expiry_date:
            return None
        today = timezone.localdate()
        if self.expiry_date < today:
            return "expired"
        days_left = (self.expiry_date - today).days
        if days_left <= 30:
            return "critical"
        if days_left <= 90:
            return "warning"
        return "ok"


class StockMovement(models.Model):
    """A log entry for every stock IN or OUT action, for a full audit trail."""

    MOVEMENT_CHOICES = [
        ("in", "Stock In"),
        ("out", "Stock Out"),
    ]

    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} - {self.variant}"
