# orders/models.py

from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils import timezone
import base64
import uuid

# ============================================================
# Payment Method Model
# ============================================================
class PaymentMethod(models.Model):
    """Payment methods - PhonePe, Paytm, Google Pay"""
    
    METHOD_CHOICES = [
        ('phonepe', 'PhonePe'),
        ('paytm', 'Paytm'),
        ('googlepay', 'Google Pay'),
        ('upi', 'UPI'),
    ]
    
    # Basic fields
    name = models.CharField(max_length=50, choices=METHOD_CHOICES, default='phonepe')
    display_name = models.CharField(max_length=50, default='', blank=True)
    receiver_number = models.CharField(max_length=50, default='', blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # Additional
    instructions = models.TextField(blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-is_default']
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.display_name}"
    
    def get_name_display(self):
        """Get display name from choices"""
        return dict(self.METHOD_CHOICES).get(self.name, self.name)
    
    def get_logo_url(self):
        """Static logo path"""
        logos = {
            'phonepe': '/static/images/payment/phonepe-logo.svg',
            'paytm': '/static/images/payment/paytm-logo.svg',
            'googlepay': '/static/images/payment/googlepay-logo.svg',
            'upi': '/static/images/payment/upi-logo.svg',
        }
        return logos.get(self.name, '/static/images/payment/default.svg')


# ============================================================
# Offer Banner Model (Image stored as Base64)
# ============================================================
class OfferBanner(models.Model):
    title = models.CharField(max_length=100, default='', blank=True)
    subtitle = models.CharField(max_length=200, blank=True, default='')
    tag_text = models.CharField(max_length=50, blank=True, default='')
    
    # Image stored as Base64
    image_base64 = models.TextField(blank=True, null=True)
    image_format = models.CharField(max_length=10, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    link_url = models.URLField(blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Offer Banner"
        verbose_name_plural = "Offer Banners"
    
    def __str__(self):
        return self.title or f"Banner {self.id}"
    
    def get_image_url(self):
        """Get image URL from Base64 data"""
        if self.image_base64:
            return f"data:image/{self.image_format or 'jpeg'};base64,{self.image_base64}"
        return None
    
    def save_image(self, image_file):
        """Save image as Base64"""
        try:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            
            # Detect format
            if image_file.name.lower().endswith('.png'):
                format_str = 'png'
            elif image_file.name.lower().endswith('.jpg') or image_file.name.lower().endswith('.jpeg'):
                format_str = 'jpeg'
            elif image_file.name.lower().endswith('.gif'):
                format_str = 'gif'
            elif image_file.name.lower().endswith('.webp'):
                format_str = 'webp'
            else:
                format_str = 'jpeg'
            
            self.image_base64 = base64_str
            self.image_format = format_str
            return True
        except Exception as e:
            print(f"Error saving banner image: {e}")
            return False
    
    def clear_image(self):
        """Clear image data"""
        self.image_base64 = None
        self.image_format = None


# ============================================================
# Order Model
# ============================================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('payment_pending', 'Payment Pending'),
        ('payment_verified', 'Payment Verified'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # User and Order Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, default='')
    
    # Shipping Details
    shipping_address = models.TextField(default='')
    shipping_city = models.CharField(max_length=100, default='')
    shipping_postal_code = models.CharField(max_length=10, default='')
    shipping_phone = models.CharField(max_length=15, default='')
    billing_address = models.TextField(blank=True, default='')
    
    # Financial
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders'
    )
    payment_method_name = models.CharField(max_length=50, blank=True, default='')
    payment_receiver_number = models.CharField(max_length=50, blank=True, default='')
    
    # Screenshot
    payment_screenshot_base64 = models.TextField(blank=True, null=True)
    payment_screenshot_format = models.CharField(max_length=10, blank=True, null=True)
    
    # Payment verification
    payment_verified_at = models.DateTimeField(blank=True, null=True)
    payment_verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_payments'
    )
    payment_notes = models.TextField(blank=True, default='')
    transaction_id = models.CharField(max_length=100, blank=True, default='')
    
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    
    @property
    def items_count(self):
        return self.items.count()
    
    @property
    def has_payment_screenshot(self):
        return bool(self.payment_screenshot_base64)
    
    def get_payment_screenshot_url(self):
        if self.payment_screenshot_base64:
            return f"data:image/{self.payment_screenshot_format or 'jpeg'};base64,{self.payment_screenshot_base64}"
        return None


# ============================================================
# Order Item Model
# ============================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


# ============================================================
# Payment Timeline Model
# ============================================================
class PaymentTimeline(models.Model):
    EVENT_CHOICES = [
        ('order_created', 'Order Created'),
        ('payment_selected', 'Payment Method Selected'),
        ('screenshot_uploaded', 'Screenshot Uploaded'),
        ('payment_verified', 'Payment Verified'),
        ('payment_rejected', 'Payment Rejected'),
        ('order_processing', 'Order Processing'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='timeline')
    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_event_display()}"