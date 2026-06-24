from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product

# ✅ home অ্যাপ থেকে Category ইমপোর্ট করো
from home.models import Category

# Wishlist import
try:
    from wishlist.models import WishlistItem
except ImportError:
    WishlistItem = None

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Wishlist status
    if WishlistItem and request.user.is_authenticated:
        try:
            wishlist_product_ids = WishlistItem.objects.filter(
                wishlist__user=request.user
            ).values_list('product_id', flat=True)
            for product in products:
                product.in_wishlist = product.id in wishlist_product_ids
        except:
            for product in products:
                product.in_wishlist = False
    else:
        for product in products:
            product.in_wishlist = False
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Wishlist status
    in_wishlist = False
    if WishlistItem and request.user.is_authenticated:
        try:
            in_wishlist = WishlistItem.objects.filter(
                wishlist__user=request.user,
                product=product
            ).exists()
        except:
            in_wishlist = False
    
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product_id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'products/product_detail.html', context)


def category_detail(request, slug):
    # home অ্যাপের Category ব্যবহার করো
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category_id=category.id, is_active=True)
    
    # Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Wishlist status
    if WishlistItem and request.user.is_authenticated:
        try:
            wishlist_product_ids = WishlistItem.objects.filter(
                wishlist__user=request.user
            ).values_list('product_id', flat=True)
            for product in products:
                product.in_wishlist = product.id in wishlist_product_ids
        except:
            for product in products:
                product.in_wishlist = False
    else:
        for product in products:
            product.in_wishlist = False
    
    # Subcategories
    subcategories = Category.objects.filter(is_active=True).exclude(id=category.id)[:5]
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
    }
    return render(request, 'products/category_detail.html', context)