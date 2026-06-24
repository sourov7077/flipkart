# wishlist/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from products.models import Product
from .models import Wishlist, WishlistItem
import logging

logger = logging.getLogger(__name__)

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.select_related('product').all()
    
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist/wishlist.html', context)

@login_required
def toggle_wishlist(request, product_id):
    """
    ✅ পারফেক্ট টগল সিস্টেম - একবার ক্লিক করলে অ্যাড, আবার ক্লিক করলে রিমুভ
    🔥 ডুপ্লিকেট এন্ট্রি প্রবলেম ১০০% সলভ!
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    try:
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # 🔥 মেইন লজিক: আগে আইটেম খুঁজি, আছে কিনা দেখি
        existing_item = WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product
        ).first()

        if existing_item:
            # ✅ ইতিমধ্যে আছে → ডিলিট করো (রিমুভ)
            existing_item.delete()
            in_wishlist = False
            message = f'{product.name} removed from wishlist'
            logger.info(f"User {request.user.username} removed {product.name} from wishlist")
        else:
            # ✅ নেই → ক্রিয়েট করো (অ্যাড)
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            in_wishlist = True
            message = f'{product.name} added to wishlist'
            logger.info(f"User {request.user.username} added {product.name} to wishlist")

        wishlist_count = wishlist.items.count()

        # 🔥 AJAX রেসপন্স
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'in_wishlist': in_wishlist,
                'message': message,
                'wishlist_count': wishlist_count,
            })

        # ✅ নন-এজ্যাক্স রেসপন্স (যদি কেউ ইউজ করে)
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_view'))

    except Product.DoesNotExist:
        logger.error(f"Product not found: {product_id}")
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)

    except IntegrityError as e:
        # 🔥 ডুপ্লিকেট এন্ট্রি (এক্সট্রা সেফটি)
        logger.error(f"IntegrityError in toggle_wishlist: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Already in wishlist'
        }, status=400)

    except Exception as e:
        logger.error(f"Wishlist toggle error: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()

    wishlist = get_object_or_404(Wishlist, user=request.user)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from wishlist!',
            'wishlist_count': wishlist.items.count(),
        })

    messages.success(request, f'{product_name} removed from wishlist!')
    return redirect('wishlist:wishlist_view')


@login_required
def wishlist_count_api(request):
    try:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        return JsonResponse({
            'count': wishlist.items.count()
        })
    except Exception as e:
        logger.error(f"Wishlist count error: {e}")
        return JsonResponse({'count': 0})


@login_required
def add_to_wishlist(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            return JsonResponse({
                'success': False,
                'message': 'Already in wishlist'
            })

        WishlistItem.objects.create(wishlist=wishlist, product=product)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to wishlist',
                'wishlist_count': wishlist.items.count()
            })

        messages.success(request, f'{product.name} added to wishlist!')
        return redirect('wishlist:wishlist_view')

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    except Exception as e:
        logger.error(f"Add to wishlist error: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)