# cart/context_processors.py
from .cart import Cart

def cart_total(request):
    """Cart total items and price for all templates"""
    try:
        cart = Cart(request)
        return {
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': str(cart.get_total_price()),  # ✅ str() Convert
        }
    except Exception as e:
        print(f"Cart context processor error: {e}")
        return {
            'cart_total_items': 0,
            'cart_total_price': '0.00',
        }