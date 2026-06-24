# orders/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Order, OrderItem, PaymentTimeline, PaymentMethod, OfferBanner


# ============================================================
# OfferBanner Admin Form (with file upload)
# ============================================================
class OfferBannerForm(forms.ModelForm):
    """Custom form for OfferBanner with file upload"""
    image_file = forms.FileField(
        required=False,
        label='Upload Image',
        help_text='Upload a banner image (JPG, PNG, GIF, WebP)'
    )
    
    class Meta:
        model = OfferBanner
        fields = ['title', 'subtitle', 'tag_text', 'image_file', 'link_url', 'is_active', 'order']
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle image upload
        if 'image_file' in self.files:
            image_file = self.files['image_file']
            instance.save_image(image_file)
        
        if commit:
            instance.save()
        return instance


# ============================================================
# PaymentMethod Admin
# ============================================================
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'display_name', 'receiver_number', 'is_active', 'is_default', 'order')
    list_filter = ('name', 'is_active')
    search_fields = ('receiver_number', 'display_name')
    list_editable = ('is_active', 'is_default', 'order')
    
    fieldsets = (
        ('Payment Method', {
            'fields': ('name', 'display_name', 'receiver_number', 'instructions')
        }),
        ('Status & Display', {
            'fields': ('is_active', 'is_default', 'order')
        }),
    )
    
    def get_name_display(self, obj):
        return obj.get_name_display()
    get_name_display.short_description = 'Payment Method'
    
    def save_model(self, request, obj, form, change):
        if not obj.display_name:
            obj.display_name = obj.get_name_display()
        super().save_model(request, obj, form, change)


# ============================================================
# OfferBanner Admin
# ============================================================
@admin.register(OfferBanner)
class OfferBannerAdmin(admin.ModelAdmin):
    form = OfferBannerForm
    list_display = ('title', 'tag_text', 'is_active', 'order', 'created_at', 'preview_banner')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active', 'order')
    
    fieldsets = (
        ('Banner Content', {
            'fields': ('title', 'subtitle', 'tag_text', 'image_file', 'link_url')
        }),
        ('Status & Display', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def preview_banner(self, obj):
        if obj.image_base64:
            return format_html(
                '<img src="data:image/{};base64,{}" style="max-height: 60px; max-width: 200px; border-radius: 4px; object-fit: cover;" />',
                obj.image_format or 'jpeg',
                obj.image_base64[:100] + '...' if len(obj.image_base64) > 100 else obj.image_base64
            )
        return format_html('<span style="color: #999;">No image</span>')
    preview_banner.short_description = 'Preview'


# ============================================================
# Order Admin
# ============================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'total')
    can_delete = False
    extra = 0


class PaymentTimelineInline(admin.TabularInline):
    model = PaymentTimeline
    readonly_fields = ('event', 'description', 'created_at', 'created_by')
    can_delete = False
    extra = 0
    fields = ('event', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'status', 'payment_status', 'get_payment_method', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method__name', 'created_at')
    search_fields = ('order_number', 'user__username', 'shipping_phone', 'transaction_id')
    readonly_fields = ('order_number', 'user', 'subtotal', 'shipping_cost', 'discount', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentTimelineInline]
    
    fieldsets = (
        ('Order Information', {'fields': ('order_number', 'user', 'status', 'payment_status')}),
        ('Shipping Details', {'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_phone')}),
        ('Billing Details', {'fields': ('billing_address',)}),
        ('Financial Information', {'fields': ('subtotal', 'shipping_cost', 'discount', 'total')}),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_method_name', 'payment_receiver_number', 
                      'payment_screenshot_base64', 'payment_screenshot_format', 
                      'payment_verified_at', 'payment_verified_by', 'payment_notes', 'transaction_id')
        }),
        ('Additional', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_payment_method(self, obj):
        return obj.payment_method_name or obj.payment_method
    get_payment_method.short_description = 'Payment Method'
    
    actions = ['mark_as_paid', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='paid', status='payment_verified')
        for order in queryset:
            PaymentTimeline.objects.create(
                order=order,
                event='payment_verified',
                description=f'Payment verified by admin {request.user.username}',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()} orders marked as paid.")
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        for order in queryset:
            PaymentTimeline.objects.create(
                order=order,
                event='order_processing',
                description=f'Order processing started by {request.user.username}',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()} orders marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        for order in queryset:
            PaymentTimeline.objects.create(
                order=order,
                event='order_shipped',
                description=f'Order shipped by {request.user.username}',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        for order in queryset:
            PaymentTimeline.objects.create(
                order=order,
                event='order_delivered',
                description=f'Order delivered by {request.user.username}',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as delivered"