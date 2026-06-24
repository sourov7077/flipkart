from django import forms
from .models import Product, Brand

# ✅ home অ্যাপ থেকে Category ইমপোর্ট করো
from home.models import Category

class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label="All Brands"
    )
    min_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    sort_by = forms.ChoiceField(
        choices=[
            ('newest', 'Newest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('name', 'Name A-Z'),
        ],
        required=False,
        initial='newest'
    )