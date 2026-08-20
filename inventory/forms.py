from django import forms

from .models import Brand, Category, Product, ProductVariant, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "brand", "category", "country_of_origin", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
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
        widgets = {
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["movement_type", "quantity", "note"]


class QuickCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class QuickBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]
