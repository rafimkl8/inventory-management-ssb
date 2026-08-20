from django.contrib import admin

from .models import Brand, Category, Product, ProductVariant, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class ProductVariantInline(admin.TabularInline):
    """Lets you add all sizes (e.g. 90ml, 400ml) right on the Product page."""

    model = ProductVariant
    extra = 1
    fields = [
        "size_label",
        "unit",
        "sku",
        "quantity_in_stock",
        "reorder_level",
        "cost_price",
        "selling_price",
        "batch_number",
        "expiry_date",
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "category", "country_of_origin"]
    list_filter = ["brand", "category", "country_of_origin"]
    search_fields = ["name", "brand__name", "category__name"]
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "size_label",
        "unit",
        "quantity_in_stock",
        "reorder_level",
        "selling_price",
        "expiry_date",
    ]
    list_filter = ["unit", "product__brand", "product__category"]
    search_fields = ["product__name", "sku", "batch_number"]
    date_hierarchy = "expiry_date"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["variant", "movement_type", "quantity", "created_at", "note"]
    list_filter = ["movement_type"]
    search_fields = ["variant__product__name"]
    date_hierarchy = "created_at"
