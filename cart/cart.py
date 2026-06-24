from decimal import Decimal
from django.conf import settings
from products.models import Product
import logging

logger = logging.getLogger(__name__)

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)  # ✅ শুধু price স্টোর, product নয়
            }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(p.id): p for p in products}

        for product_id, item in self.cart.items():
            item_copy = item.copy()  # IMPORTANT - মূল item পরিবর্তন না করে কপি তৈরি করুন

            if product_id in product_dict:
                item_copy['product'] = product_dict[product_id]
                item_copy['total_price'] = (
                    Decimal(str(item_copy['price'])) *
                    item_copy['quantity']
                )
                yield item_copy

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        try:
            return sum(Decimal(str(item['price'])) * item['quantity'] for item in self.cart.values())
        except Exception as e:
            logger.error(f"Cart total price error: {e}")
            return Decimal('0.00')

    def get_total_items(self):
        try:
            return sum(item['quantity'] for item in self.cart.values())
        except Exception as e:
            logger.error(f"Cart total items error: {e}")
            return 0

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True
        self.cart = {}

    def get_items(self):
        items = []
        for item in self:
            items.append(item)
        return items