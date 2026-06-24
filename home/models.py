from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import base64
import imghdr

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='shopping-bag')
    icon_color = models.CharField(max_length=20, default='#2874f0')
    bg_color = models.CharField(max_length=20, default='#f0f0f0')
    image_base64 = models.TextField(blank=True, null=True)  # ✅ আইকন ইমেজ
    image_format = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['-is_default', 'order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_image_url(self):
        if self.image_base64 and self.image_format:
            return f"data:image/{self.image_format};base64,{self.image_base64}"
        return None
    
    def save_image(self, image_file):
        try:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            format_str = imghdr.what(None, h=image_data) or 'jpeg'
            self.image_base64 = base64_str
            self.image_format = format_str
            self.save()
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def get_products(self):
        try:
            from products.models import Product
            return Product.objects.filter(category=self, is_active=True)
        except ImportError:
            return []
    
    def get_slider_images(self):
        return self.slider_images.filter(is_active=True)


class CategorySliderImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='slider_images')
    title = models.CharField(max_length=100, blank=True, null=True)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    image_base64 = models.TextField(blank=True, null=True)
    image_format = models.CharField(max_length=10, blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Category Slider Image'
        verbose_name_plural = 'Category Slider Images'
    
    def __str__(self):
        return f"{self.category.name} - {self.title or 'Slider'}"
    
    def get_image_url(self):
        if self.image_base64 and self.image_format:
            return f"data:image/{self.image_format};base64,{self.image_base64}"
        return None
    
    def save_image(self, image_file):
        try:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            format_str = imghdr.what(None, h=image_data) or 'jpeg'
            self.image_base64 = base64_str
            self.image_format = format_str
            self.save()
            return True
        except Exception as e:
            print(f"Error saving slider image: {e}")
            return False


class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='location')
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.city}"