# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .cart import Cart
import logging

logger = logging.getLogger(__name__)


def cart_detail(request):
    cart = Cart(request)
    cart_items = []
    for item in cart:
        if 'product' in item and item['product']:
            cart_items.append({
                'product': item['product'],
                'quantity': item['quantity'],
                'total_price': item['total_price']
            })
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'total_price': cart.get_total_price(),
    }
    return render(request, 'cart/detail.html', context)


def cart_add_ajax(request):
    """AJAX দিয়ে কার্টে আইটেম যোগ করুন"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            })
        
        try:
            product = Product.objects.get(id=product_id)
            cart = Cart(request)
            
            if quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Sorry, only {product.stock} items available.'
                })
            
            cart.add(product=product, quantity=quantity)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ {product.name} added to cart!',
                'cart_total_items': cart.get_total_items(),
                'cart_total_price': str(cart.get_total_price()),
                'item_count': cart.get_total_items()
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    })


# ✅ এই ফাংশনটা ইম্পরট্যান্ট! 
def cart_add(request, product_id):
    """
    Non-AJAX: কার্টে আইটেম যোগ করুন
    কিন্তু যদি AJAX রিকোয়েস্ট হয়, JSON রিটার্ন করবে
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available.')
        # AJAX চেক
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Sorry, only {product.stock} items available.'
            })
        return redirect('products:product_detail', id=product_id)
    
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'✅ {product.name} added to cart!')
    
    # ✅ AJAX রিকোয়েস্ট চেক (এই লাইনটা আগে ছিল না, এটাই সমস্যা ছিল)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'✅ {product.name} added to cart!',
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': str(cart.get_total_price())
        })
    
    return redirect('cart:cart_detail')


def cart_remove_ajax(request):
    """AJAX দিয়ে কার্ট থেকে আইটেম রিমুভ করুন"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            })
        
        try:
            product = Product.objects.get(id=product_id)
            cart = Cart(request)
            cart.remove(product)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ {product.name} removed from cart!',
                'cart_total_items': cart.get_total_items(),
                'cart_total_price': str(cart.get_total_price())
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    })


def cart_remove(request, product_id):
    """Non-AJAX: কার্ট থেকে আইটেম রিমুভ করুন"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, '✅ Item removed from cart!')
    return redirect('cart:cart_detail')


def cart_update_ajax(request):
    """AJAX দিয়ে কার্ট আপডেট করুন"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        
        if not product_id or not action:
            return JsonResponse({
                'success': False,
                'message': 'Product ID and action are required'
            })
        
        try:
            product = Product.objects.get(id=product_id)
            cart = Cart(request)
            
            if action == 'increase':
                cart.add(product=product, quantity=1)
                message = f'✅ Quantity increased for {product.name}'
            elif action == 'decrease':
                current_qty = 0
                for item in cart:
                    if str(item['product'].id) == str(product.id):
                        current_qty = item['quantity']
                        break
                
                if current_qty <= 1:
                    cart.remove(product)
                    message = f'✅ {product.name} removed from cart!'
                else:
                    cart.add(product=product, quantity=-1)
                    message = f'✅ Quantity decreased for {product.name}'
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action.'
                })
            
            cart_items = []
            for item in cart:
                if 'product' in item and item['product']:
                    cart_items.append({
                        'product_id': item['product'].id,
                        'product_name': item['product'].name,
                        'quantity': item['quantity'],
                        'total_price': str(item['total_price'])
                    })
            
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total_items': cart.get_total_items(),
                'cart_total_price': str(cart.get_total_price()),
                'cart_items': cart_items,
                'is_empty': len(cart) == 0
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    })


def cart_update(request, product_id):
    """
    Non-AJAX: কার্ট আপডেট করুন
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action')
    
    if action == 'increase':
        cart.add(product=product, quantity=1)
        messages.success(request, f'✅ Quantity increased for {product.name}')
    elif action == 'decrease':
        current_qty = 0
        for item in cart:
            if str(item['product'].id) == str(product.id):
                current_qty = item['quantity']
                break
        
        if current_qty <= 1:
            cart.remove(product)
            messages.success(request, f'✅ {product.name} removed from cart!')
        else:
            cart.add(product=product, quantity=-1)
            messages.success(request, f'✅ Quantity decreased for {product.name}')
    
    return redirect('cart:cart_detail')


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, '✅ Cart cleared successfully!')
    return redirect('cart:cart_detail')


def cart_count_api(request):
    try:
        cart = Cart(request)
        return JsonResponse({
            'success': True,
            'count': cart.get_total_items(),
            'total': str(cart.get_total_price())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'count': 0,
            'total': '0.00'
        })


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, '⚠️ Your cart is empty!')
        return redirect('cart:cart_detail')
    return redirect('orders:order_create')