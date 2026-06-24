from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from .models import Coupon

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'Please enter coupon code'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            cart = Cart(request)
            cart_total = cart.get_total_price()
            
            if coupon.is_valid():
                if cart_total < coupon.min_purchase:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Minimum purchase amount is ৳{coupon.min_purchase}'
                    })
                
                discount = coupon.calculate_discount(cart_total)
                
                if discount == 0:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Coupon is not applicable for this order'
                    })
                
                request.session['applied_coupon'] = {
                    'code': coupon.code,
                    'discount': float(discount),
                    'type': coupon.discount_type,
                    'value': float(coupon.discount_value)
                }
                
                return JsonResponse({
                    'success': True,
                    'message': 'Coupon applied successfully!',
                    'discount': float(discount),
                    'new_total': float(cart_total - discount)
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Coupon is not valid or expired'
                })
                
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def remove_coupon(request):
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        return JsonResponse({'success': True, 'message': 'Coupon removed'})
    return JsonResponse({'success': False, 'message': 'No coupon applied'})