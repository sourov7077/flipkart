from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Category, CategorySliderImage, UserLocation
import base64
import imghdr


class CategorySliderImageInlineForm(forms.ModelForm):
    image_upload = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text="Upload slider image (JPG, PNG, GIF, WEBP) - Max 5MB"
    )
    
    class Meta:
        model = CategorySliderImage
        fields = ['title', 'subtitle', 'link_url', 'is_active', 'order']
    
    def clean_image_upload(self):
        image = self.cleaned_data.get('image_upload')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large ( > 5MB )')
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError('Only JPEG, PNG, GIF and WEBP images are allowed')
        return image
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'image_upload' in self.cleaned_data and self.cleaned_data['image_upload']:
            image_file = self.cleaned_data['image_upload']
            try:
                image_data = image_file.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')
                format_str = imghdr.what(None, h=image_data) or 'jpeg'
                instance.image_base64 = base64_str
                instance.image_format = format_str
            except Exception as e:
                print(f"Error processing image: {e}")
        
        if commit:
            instance.save()
        return instance


class CategorySliderImageInline(admin.TabularInline):
    model = CategorySliderImage
    form = CategorySliderImageInlineForm
    extra = 1
    fields = ['image_upload', 'title', 'subtitle', 'link_url', 'is_active', 'order', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image_base64:
            return f'<img src="{obj.get_image_url()}" style="max-width: 120px; max-height: 70px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd; padding: 2px;">'
        return '<span style="color: #999; font-size: 13px;">No image uploaded</span>'
    preview.allow_tags = True
    preview.short_description = 'Preview'


class CategoryAdminForm(forms.ModelForm):
    image_upload = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text="Upload category icon image (JPG, PNG, GIF, WEBP) - Max 2MB"
    )
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            existing = Category.objects.filter(name=name)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise ValidationError(f'Category with name "{name}" already exists!')
        return name
    
    def clean_image_upload(self):
        image = self.cleaned_data.get('image_upload')
        if image:
            if image.size > 2 * 1024 * 1024:
                raise ValidationError('Image file too large ( > 2MB )')
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError('Only JPEG, PNG, GIF and WEBP images are allowed')
        return image
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'image_upload' in self.cleaned_data and self.cleaned_data['image_upload']:
            image_file = self.cleaned_data['image_upload']
            try:
                image_data = image_file.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')
                format_str = imghdr.what(None, h=image_data) or 'jpeg'
                instance.image_base64 = base64_str
                instance.image_format = format_str
            except Exception as e:
                print(f"Error processing image: {e}")
        
        if commit:
            instance.save()
        return instance


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ('name', 'slug', 'is_default', 'order', 'is_active', 'icon', 'icon_preview', 'slider_count')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active', 'is_default')
    readonly_fields = ('icon_preview', 'slider_count')
    inlines = [CategorySliderImageInline]
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'description', 'order')
        }),
        ('Default Settings', {
            'fields': ('is_default',),
            'description': '✅ Check this to keep this category always on top (For You)'
        }),
        ('Icon Settings', {
            'fields': ('icon', 'icon_color', 'bg_color', 'image_upload', 'icon_preview')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def icon_preview(self, obj):
        if obj.image_base64:
            return f'<img src="{obj.get_image_url()}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #2874f0; padding: 2px;">'
        return '<span style="color: #999; font-size: 13px;">No icon</span>'
    icon_preview.allow_tags = True
    icon_preview.short_description = 'Icon Preview'
    
    def slider_count(self, obj):
        count = obj.slider_images.filter(is_active=True).count()
        return f'📸 {count} images'
    slider_count.short_description = 'Sliders'
    
    def save_model(self, request, obj, form, change):
        if obj.is_default:
            Category.objects.filter(is_default=True).exclude(id=obj.id).update(is_default=False)
        super().save_model(request, obj, form, change)


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'area', 'created_at', 'updated_at')
    list_filter = ('city',)
    search_fields = ('user__username', 'user__email', 'city', 'area')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Location Information', {
            'fields': ('city', 'area', 'latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )