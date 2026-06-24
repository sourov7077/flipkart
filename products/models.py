from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
import base64
import imghdr

# ✅ home অ্যাপ থেকে Category ইমপোর্ট করো
from home.models import Category

# products/models.py

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey('home.Category', on_delete=models.CASCADE, related_name='brands', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    # ✅ home অ্যাপের Category ব্যবহার করো
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Base64 image field (to avoid file system errors)
    image_base64 = models.TextField(blank=True, null=True)
    image_format = models.CharField(max_length=10, blank=True, null=True)
    
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def discount_percentage(self):
        if self.old_price and float(self.old_price) > 0:
            discount = ((float(self.old_price) - float(self.price)) / float(self.old_price)) * 100
            return round(discount, 0)
        return 0
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    def get_image_url(self):
        """Generate data URL from base64 image"""
        if self.image_base64 and self.image_format:
            return f"data:image/{self.image_format};base64,{self.image_base64}"
        return None
    
    def save_image(self, image_file):
        """Save image as base64 string"""
        try:
            # Read image file
            image_data = image_file.read()
            
            # Convert to base64
            base64_str = base64.b64encode(image_data).decode('utf-8')
            
            # Determine format
            format_str = imghdr.what(None, h=image_data)
            if not format_str:
                # Default to jpeg
                format_str = 'jpeg'
            
            self.image_base64 = base64_str
            self.image_format = format_str
            self.save()
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_base64 = models.TextField(blank=True, null=True)
    image_format = models.CharField(max_length=10, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def get_image_url(self):
        if self.image_base64 and self.image_format:
            return f"data:image/{self.image_format};base64,{self.image_base64}"
        return None