from django import forms
from .models import Order, PaymentMethod

class OrderCreateForm(forms.ModelForm):
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        empty_label=None,
        required=True,
        label="Select Payment Method"
    )
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_phone',
                 'billing_address', 'payment_method', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'House/Flat, Street, Area'}),
            'billing_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Same as shipping address or enter different'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Any special instructions for delivery'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_method = PaymentMethod.objects.filter(is_active=True, is_default=True).first()
        if default_method:
            self.fields['payment_method'].initial = default_method