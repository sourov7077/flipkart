from django import template
from home.models import Category

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None:
        return []
    return dictionary.get(key, [])

@register.inclusion_tag('components/category_tabs.html', takes_context=True)
def category_tabs(context, active_slug=None):
    """ডাইনামিক ক্যাটাগরি ট্যাব রেন্ডার করার জন্য"""
    categories = Category.objects.filter(is_active=True).exclude(slug='for-you')
    
    # প্রতিটি ক্যাটাগরিতে প্রোডাক্ট কাউন্ট যোগ করো
    for category in categories:
        category.product_count = category.products.filter(is_active=True).count()
    
    # All Products কাউন্ট
    try:
        from products.models import Product
        total_products = Product.objects.filter(is_active=True).count()
    except:
        total_products = 0
    
    return {
        'categories': categories,
        'active_slug': active_slug,
        'total_products': total_products,
    }