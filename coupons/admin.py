from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_purchase', 'valid_from', 'valid_to', 'is_active', 'used_count')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)