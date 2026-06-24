# orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Count
from datetime import timedelta
import uuid
from decimal import Decimal

from cart.cart import Cart
from .models import Order, OrderItem, PaymentTimeline, PaymentMethod, OfferBanner
from .forms import OrderCreateForm
from products.models import Product


# ============================================================
# ORDER CREATE
# ============================================================
@login_required
def order_create(request):
    cart = Cart(request)
    
    # Check if cart is empty
    if len(cart) == 0:
        messages.warning(request, '⚠️ Your cart is empty!')
        return redirect('cart:cart_detail')
    
    # Get active payment methods
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Get active banners
    active_banners = OfferBanner.objects.filter(is_active=True).order_by('order')
    
    # Get applied coupon from session
    applied_coupon = request.session.get('applied_coupon')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        
        # Get form data
        shipping_address = request.POST.get('shipping_address', '').strip()
        shipping_city = request.POST.get('shipping_city', '').strip()
        shipping_postal_code = request.POST.get('shipping_postal_code', '').strip()
        shipping_phone = request.POST.get('shipping_phone', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        
        # Validate required fields
        if not full_name:
            messages.error(request, '❌ Please enter your full name.')
            return render(request, 'orders/order_create.html', {
                'form': form,
                'cart': cart,
                'payment_methods': payment_methods,
                'active_banners': active_banners,
                'applied_coupon': applied_coupon,
            })
        
        if not shipping_address:
            messages.error(request, '❌ Please enter your shipping address.')
            return render(request, 'orders/order_create.html', {
                'form': form,
                'cart': cart,
                'payment_methods': payment_methods,
                'active_banners': active_banners,
                'applied_coupon': applied_coupon,
            })
        
        if not shipping_city:
            messages.error(request, '❌ Please enter your city.')
            return render(request, 'orders/order_create.html', {
                'form': form,
                'cart': cart,
                'payment_methods': payment_methods,
                'active_banners': active_banners,
                'applied_coupon': applied_coupon,
            })
        
        if not shipping_postal_code:
            messages.error(request, '❌ Please enter your postal code.')
            return render(request, 'orders/order_create.html', {
                'form': form,
                'cart': cart,
                'payment_methods': payment_methods,
                'active_banners': active_banners,
                'applied_coupon': applied_coupon,
            })
        
        if not shipping_phone or len(shipping_phone) < 10:
            messages.error(request, '❌ Please enter a valid phone number (min 10 digits).')
            return render(request, 'orders/order_create.html', {
                'form': form,
                'cart': cart,
                'payment_methods': payment_methods,
                'active_banners': active_banners,
                'applied_coupon': applied_coupon,
            })
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Calculate totals
                    subtotal = Decimal(str(cart.get_total_price()))
                    shipping_cost = Decimal('60.00') if subtotal < Decimal('1000.00') else Decimal('0.00')
                    
                    discount = Decimal('0.00')
                    if applied_coupon:
                        discount = Decimal(str(applied_coupon.get('discount', 0)))
                    
                    total = subtotal + shipping_cost - discount
                    
                    # Create order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.order_number = str(uuid.uuid4())[:20].replace('-', '').upper()
                    order.subtotal = subtotal
                    order.shipping_cost = shipping_cost
                    order.discount = discount
                    order.total = total
                    order.status = 'payment_pending'
                    order.payment_status = 'pending'
                    
                    # Save payment method info
                    payment_method = form.cleaned_data.get('payment_method')
                    if payment_method:
                        order.payment_method = payment_method
                        order.payment_method_name = payment_method.get_name_display()
                        order.payment_receiver_number = payment_method.receiver_number  # Hidden from user
                    
                    order.save()
                    
                    # Create order items
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            product_name=item['product'].name,
                            price=Decimal(str(item['price'])),
                            quantity=item['quantity'],
                            total=Decimal(str(item['total_price']))
                        )
                    
                    # Create timeline entry
                    PaymentTimeline.objects.create(
                        order=order,
                        event='order_created',
                        description=f'Order created by {request.user.username}',
                        created_by=request.user
                    )
                    
                    # Clear cart and coupon
                    cart.clear()
                    if 'applied_coupon' in request.session:
                        del request.session['applied_coupon']
                    
                    messages.success(request, f'✅ Order #{order.order_number} created successfully!')
                    return redirect('orders:order_detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, f'❌ Error creating order: {str(e)}')
                return redirect('cart:cart_detail')
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        # GET request - prefill form with user profile data
        initial_data = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            if profile.phone:
                initial_data['shipping_phone'] = profile.phone
            if profile.address:
                initial_data['shipping_address'] = profile.address
            if profile.city:
                initial_data['shipping_city'] = profile.city
            if profile.postal_code:
                initial_data['shipping_postal_code'] = profile.postal_code
        
        form = OrderCreateForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'payment_methods': payment_methods,
        'active_banners': active_banners,
        'applied_coupon': applied_coupon,
    }
    return render(request, 'orders/order_create.html', context)


# ============================================================
# ORDER DETAIL
# ============================================================
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    timeline = order.timeline.all()
    
    context = {
        'order': order,
        'timeline': timeline,
    }
    return render(request, 'orders/order_detail.html', context)


# ============================================================
# ORDER HISTORY
# ============================================================
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)


# ============================================================
# ADMIN DASHBOARD
# ============================================================



@staff_member_required
def admin_dashboard(request):
    # Stats
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total'))['total__sum'] or 0
    pending_orders = Order.objects.filter(status='pending').count()
    payment_pending = Order.objects.filter(status='payment_pending').count()
    total_users = User.objects.count()  # ✅ এখন কাজ করবে
    
    # Weekly stats
    week_ago = timezone.now() - timedelta(days=7)
    weekly_orders = Order.objects.filter(created_at__gte=week_ago).count()
    weekly_revenue = Order.objects.filter(created_at__gte=week_ago).aggregate(Sum('total'))['total__sum'] or 0
    
    # Today stats
    today_orders = Order.objects.filter(created_at__date=timezone.now().date()).count()
    
    # ✅ Top products - ফিক্সড
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Payment pending orders
    payment_pending_orders = Order.objects.filter(
        status='payment_pending', 
        payment_status='pending'
    ).order_by('created_at')[:10]
    
    # Chart data (last 7 days)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        chart_labels.append(date.strftime('%a'))
        daily_total = Order.objects.filter(
            created_at__date=date
        ).aggregate(Sum('total'))['total__sum'] or 0
        chart_data.append(float(daily_total))
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'payment_pending': payment_pending,
        'total_users': total_users,
        'weekly_orders': weekly_orders,
        'weekly_revenue': weekly_revenue,
        'today_orders': today_orders,
        'top_products': top_products,
        'payment_pending_orders': payment_pending_orders,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'orders/admin_dashboard.html', context)


# ============================================================
# MARK ORDER AS PAID (AJAX)
# ============================================================
@login_required
def mark_order_as_paid(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if order.payment_status == 'paid':
            return JsonResponse({
                'success': True, 
                'message': 'Already paid'
            })
        
        # Update order
        order.payment_status = 'paid'
        order.status = 'processing'
        order.payment_verified_at = timezone.now()
        order.payment_verified_by = request.user
        order.save()
        
        # Create timeline
        PaymentTimeline.objects.create(
            order=order,
            event='payment_verified',
            description=f'Payment verified by {request.user.username}',
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Payment marked as paid successfully'
        })
    
    return JsonResponse({
        'success': False, 
        'message': 'Invalid request method'
    })


# ============================================================
# ADMIN - MARK ORDER STATUS (Bulk Actions)
# ============================================================
@staff_member_required
def admin_mark_status(request):
    """Bulk status update for admin"""
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids[]')
        status = request.POST.get('status')
        
        if not order_ids or not status:
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            })
        
        try:
            orders = Order.objects.filter(id__in=order_ids)
            count = orders.count()
            
            for order in orders:
                order.status = status
                order.save()
                
                # Add timeline entry
                event_map = {
                    'processing': 'order_processing',
                    'shipped': 'order_shipped',
                    'delivered': 'order_delivered',
                    'cancelled': 'order_cancelled',
                }
                event = event_map.get(status, 'order_created')
                PaymentTimeline.objects.create(
                    order=order,
                    event=event,
                    description=f'Status updated to {status} by admin {request.user.username}',
                    created_by=request.user
                )
            
            return JsonResponse({
                'success': True,
                'message': f'{count} orders updated to {status}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


# ============================================================
# ADMIN - BANNER MANAGEMENT (CRUD via AJAX)
# ============================================================
@staff_member_required
def admin_banner_list(request):
    """List all banners for admin"""
    banners = OfferBanner.objects.all().order_by('order')
    return render(request, 'orders/admin_banner_list.html', {'banners': banners})


@staff_member_required
def admin_banner_create(request):
    """Create new banner via AJAX"""
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle', '')
        tag_text = request.POST.get('tag_text', '')
        link_url = request.POST.get('link_url', '')
        is_active = request.POST.get('is_active') == 'on'
        order = request.POST.get('order', 0)
        
        banner = OfferBanner(
            title=title,
            subtitle=subtitle,
            tag_text=tag_text,
            link_url=link_url,
            is_active=is_active,
            order=order
        )
        
        # Handle image upload
        if 'image_file' in request.FILES:
            image_file = request.FILES['image_file']
            banner.save_image(image_file)
        
        banner.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Banner created successfully',
            'banner_id': banner.id
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@staff_member_required
def admin_banner_delete(request, banner_id):
    """Delete banner via AJAX"""
    if request.method == 'POST':
        banner = get_object_or_404(OfferBanner, id=banner_id)
        banner.delete()
        return JsonResponse({
            'success': True,
            'message': 'Banner deleted successfully'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@staff_member_required
def admin_banner_toggle(request, banner_id):
    """Toggle banner active status via AJAX"""
    if request.method == 'POST':
        banner = get_object_or_404(OfferBanner, id=banner_id)
        banner.is_active = not banner.is_active
        banner.save()
        return JsonResponse({
            'success': True,
            'message': f'Banner {"activated" if banner.is_active else "deactivated"}',
            'is_active': banner.is_active
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


# ============================================================
# ADMIN - PAYMENT METHOD MANAGEMENT (CRUD via AJAX)
# ============================================================
@staff_member_required
def admin_payment_method_list(request):
    """List all payment methods for admin"""
    methods = PaymentMethod.objects.all().order_by('order')
    return render(request, 'orders/admin_payment_method_list.html', {'methods': methods})


@staff_member_required
def admin_payment_method_toggle(request, method_id):
    """Toggle payment method active status via AJAX"""
    if request.method == 'POST':
        method = get_object_or_404(PaymentMethod, id=method_id)
        method.is_active = not method.is_active
        method.save()
        return JsonResponse({
            'success': True,
            'message': f'Payment method {"activated" if method.is_active else "deactivated"}',
            'is_active': method.is_active
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@staff_member_required
def admin_payment_method_delete(request, method_id):
    """Delete payment method via AJAX"""
    if request.method == 'POST':
        method = get_object_or_404(PaymentMethod, id=method_id)
        method.delete()
        return JsonResponse({
            'success': True,
            'message': 'Payment method deleted successfully'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })