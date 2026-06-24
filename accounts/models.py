from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import base64
from django.core.files.base import ContentFile
from PIL import Image
import io

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    
    # Image field - base64 encoded string
    profile_picture_base64 = models.TextField(blank=True, null=True)
    
    # Store image format
    profile_picture_format = models.CharField(max_length=10, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def has_profile_picture(self):
        return bool(self.profile_picture_base64)
    
    def get_profile_picture_url(self):
        if self.profile_picture_base64:
            return f"data:image/{self.profile_picture_format or 'jpeg'};base64,{self.profile_picture_base64}"
        return None
    
    def save_profile_picture(self, image_file):
        """Save image as base64 string"""
        import base64
        from PIL import Image
        import io
        
        # Read image file
        image_data = image_file.read()
        
        # Convert to base64
        base64_str = base64.b64encode(image_data).decode('utf-8')
        
        # Save format
        if image_file.name.lower().endswith('.png'):
            format_str = 'png'
        elif image_file.name.lower().endswith('.jpg') or image_file.name.lower().endswith('.jpeg'):
            format_str = 'jpeg'
        elif image_file.name.lower().endswith('.gif'):
            format_str = 'gif'
        else:
            format_str = 'jpeg'
        
        self.profile_picture_base64 = base64_str
        self.profile_picture_format = format_str
        self.save()
    
    def clear_profile_picture(self):
        """Remove profile picture"""
        self.profile_picture_base64 = None
        self.profile_picture_format = None
        self.save()

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

# Signal to create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)