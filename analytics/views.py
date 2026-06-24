# analytics/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import User


@staff_member_required
def admin_dashboard(request):
    """Admin analytics dashboard - শুধু অ্যাডমিন/স্টাফ দেখতে পাবে"""
    
    # Time periods
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # ✅ Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    weekly_orders = Order.objects.filter(created_at__gte=week_ago).count()
    
    # ✅ Revenue statistics - ফিক্সড (KeyError)
    total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
    weekly_revenue = Order.objects.filter(
        created_at__gte=week_ago,
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # ✅ Product statistics
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:10]
    
    low_stock = Product.objects.filter(stock__lt=10, is_active=True)[:10]
    
    # ✅ User statistics
    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    
    # ✅ Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # ✅ Chart data (last 7 days) - ফিক্সড
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%a'))
        daily_total = Order.objects.filter(
            created_at__date=date
        ).aggregate(total=Sum('total'))['total'] or 0  # ✅ ['total'] না হয়ে ['total'] ব্যবহার করছি
        chart_data.append(float(daily_total))
    
    context = {
        # Orders
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_orders': today_orders,
        'weekly_orders': weekly_orders,
        
        # Revenue
        'total_revenue': total_revenue,
        'weekly_revenue': weekly_revenue,
        
        # Products
        'top_products': top_products,
        'low_stock': low_stock,
        
        # Users
        'total_users': total_users,
        'new_users_week': new_users_week,
        
        # Recent data
        'recent_orders': recent_orders,
        
        # Chart data
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        
        # Today (for template)
        'today': today,
    }
    
    return render(request, 'analytics/dashboard.html', context)