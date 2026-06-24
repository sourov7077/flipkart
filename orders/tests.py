# orders/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem, PaymentMethod, OfferBanner, PaymentTimeline
from products.models import Product, Category
from cart.cart import Cart


class OrderModelTest(TestCase):
    """Test Order Model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.payment_method = PaymentMethod.objects.create(
            name='phonepe',
            display_name='PhonePe',
            receiver_number='9876543210@upi',
            is_active=True,
            is_default=True
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=99.99,
            stock=10,
            description='Test description'
        )
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD123456',
            shipping_address='123 Test St',
            shipping_city='Test City',
            shipping_postal_code='110001',
            shipping_phone='9876543210',
            subtotal=99.99,
            shipping_cost=0.00,
            discount=0.00,
            total=99.99,
            status='pending',
            payment_status='pending',
            payment_method=self.payment_method,
            payment_method_name='PhonePe'
        )
        
    def test_order_creation(self):
        """Test order is created successfully"""
        self.assertEqual(self.order.user.username, 'testuser')
        self.assertEqual(self.order.order_number, 'ORD123456')
        self.assertEqual(self.order.total, Decimal('99.99'))
        self.assertEqual(self.order.status, 'pending')
        
    def test_order_str_method(self):
        """Test order string representation"""
        expected = f"Order #ORD123456 - testuser"
        self.assertEqual(str(self.order), expected)
        
    def test_order_items_count_property(self):
        """Test items_count property"""
        self.assertEqual(self.order.items_count, 0)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name='Test Product',
            price=99.99,
            quantity=2,
            total=199.98
        )
        self.assertEqual(self.order.items_count, 1)
        
    def test_has_payment_screenshot(self):
        """Test has_payment_screenshot property"""
        self.assertFalse(self.order.has_payment_screenshot)
        self.order.payment_screenshot_base64 = 'test_base64_data'
        self.order.save()
        self.assertTrue(self.order.has_payment_screenshot)
        
    def test_get_payment_screenshot_url(self):
        """Test get_payment_screenshot_url method"""
        self.assertIsNone(self.order.get_payment_screenshot_url())
        self.order.payment_screenshot_base64 = 'test_data'
        self.order.payment_screenshot_format = 'png'
        self.order.save()
        expected = "data:image/png;base64,test_data"
        self.assertEqual(self.order.get_payment_screenshot_url(), expected)


class OrderItemModelTest(TestCase):
    """Test OrderItem Model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=50.00,
            stock=5,
            description='Test'
        )
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD123',
            shipping_address='Test',
            shipping_city='Test',
            shipping_postal_code='123456',
            shipping_phone='1234567890',
            subtotal=100.00,
            total=100.00
        )
        
    def test_order_item_auto_total(self):
        """Test that order item total is auto-calculated"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name='Test Product',
            price=50.00,
            quantity=3
        )
        self.assertEqual(item.total, Decimal('150.00'))
        
    def test_order_item_str(self):
        """Test order item string representation"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name='Test Product',
            price=50.00,
            quantity=2
        )
        self.assertEqual(str(item), "2 x Test Product")


class PaymentMethodModelTest(TestCase):
    """Test PaymentMethod Model"""
    
    def test_payment_method_creation(self):
        """Test payment method creation"""
        method = PaymentMethod.objects.create(
            name='phonepe',
            display_name='PhonePe',
            receiver_number='test@upi',
            is_active=True
        )
        self.assertEqual(method.get_name_display(), 'PhonePe')
        self.assertTrue(method.is_active)
        self.assertEqual(method.get_logo_url(), '/static/images/payment/phonepe-logo.svg')
        
    def test_payment_method_str(self):
        """Test string representation"""
        method = PaymentMethod.objects.create(
            name='paytm',
            display_name='Paytm'
        )
        expected = "Paytm - Paytm"
        self.assertEqual(str(method), expected)
        
    def test_default_order(self):
        """Test default ordering"""
        method1 = PaymentMethod.objects.create(name='phonepe', order=2)
        method2 = PaymentMethod.objects.create(name='paytm', order=1)
        methods = PaymentMethod.objects.all()
        self.assertEqual(methods[0], method2)
        self.assertEqual(methods[1], method1)


class OfferBannerModelTest(TestCase):
    """Test OfferBanner Model"""
    
    def test_banner_creation(self):
        """Test banner creation"""
        banner = OfferBanner.objects.create(
            title='Test Banner',
            subtitle='Test Subtitle',
            tag_text='🔥 Offer',
            is_active=True
        )
        self.assertEqual(banner.title, 'Test Banner')
        self.assertTrue(banner.is_active)
        self.assertIsNone(banner.get_image_url())
        
    def test_banner_str_without_title(self):
        """Test string representation without title"""
        banner = OfferBanner.objects.create()
        self.assertTrue(str(banner).startswith('Banner '))
        
    def test_banner_str_with_title(self):
        """Test string representation with title"""
        banner = OfferBanner.objects.create(title='My Banner')
        self.assertEqual(str(banner), 'My Banner')
        
    def test_save_image(self):
        """Test image saving as base64"""
        banner = OfferBanner.objects.create(title='Test')
        # Mock image file
        from django.core.files.uploadedfile import SimpleUploadedFile
        image_file = SimpleUploadedFile('test.jpg', b'fake_image_data', content_type='image/jpeg')
        result = banner.save_image(image_file)
        self.assertTrue(result)
        self.assertIsNotNone(banner.image_base64)
        self.assertEqual(banner.image_format, 'jpeg')


class PaymentTimelineModelTest(TestCase):
    """Test PaymentTimeline Model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD123',
            shipping_address='Test',
            shipping_city='Test',
            shipping_postal_code='123456',
            shipping_phone='1234567890',
            subtotal=100.00,
            total=100.00
        )
        
    def test_timeline_creation(self):
        """Test timeline entry creation"""
        timeline = PaymentTimeline.objects.create(
            order=self.order,
            event='order_created',
            description='Order created',
            created_by=self.user
        )
        self.assertEqual(timeline.event, 'order_created')
        self.assertEqual(timeline.created_by, self.user)
        self.assertEqual(str(timeline), f"ORD123 - Order Created")


class OrderCreateViewTest(TestCase):
    """Test Order Create View"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=99.99,
            stock=10,
            description='Test'
        )
        self.payment_method = PaymentMethod.objects.create(
            name='phonepe',
            display_name='PhonePe',
            receiver_number='test@upi',
            is_active=True,
            is_default=True
        )
        
    def test_order_create_page_requires_login(self):
        """Test that order page requires login"""
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        
    def test_order_create_page_with_empty_cart(self):
        """Test order page with empty cart"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart/')
        
    def test_order_create_with_valid_data(self):
        """Test order creation with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add item to cart
        session = self.client.session
        cart = Cart(self.client)
        cart.add(self.product, 2)
        session.save()
        
        # Submit order
        data = {
            'full_name': 'Test User',
            'shipping_address': '123 Test Street',
            'shipping_city': 'Test City',
            'shipping_postal_code': '110001',
            'shipping_phone': '9876543210',
            'shipping_state': 'Delhi',
            'shipping_address_line2': 'Near Test',
            'payment_method': str(self.payment_method.id),
        }
        
        response = self.client.post(reverse('orders:order_create'), data)
        
        # Should redirect to order detail
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/orders/'))
        
        # Check order was created
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total, Decimal('199.98'))  # 2 x 99.99
        self.assertEqual(order.order_number, 'ORD123456')  # This will fail if not created
        
    def test_order_create_with_missing_fields(self):
        """Test order creation with missing required fields"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add item to cart
        session = self.client.session
        cart = Cart(self.client)
        cart.add(self.product, 1)
        session.save()
        
        # Submit with missing data
        data = {
            'full_name': '',  # Missing
            'shipping_address': '123 Test Street',
            'shipping_city': 'Test City',
            'shipping_postal_code': '110001',
            'shipping_phone': '9876543210',
        }
        
        response = self.client.post(reverse('orders:order_create'), data)
        
        # Should stay on page with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter your full name')
        
    def test_order_create_invalid_pincode(self):
        """Test order creation with invalid pincode"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart(self.client)
        cart.add(self.product, 1)
        cart.save()
        
        data = {
            'full_name': 'Test User',
            'shipping_address': '123 Test Street',
            'shipping_city': 'Test City',
            'shipping_postal_code': '1234',  # Invalid
            'shipping_phone': '9876543210',
        }
        
        response = self.client.post(reverse('orders:order_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid 6-digit pincode')
        
    def test_order_create_invalid_phone(self):
        """Test order creation with invalid phone"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart(self.client)
        cart.add(self.product, 1)
        cart.save()
        
        data = {
            'full_name': 'Test User',
            'shipping_address': '123 Test Street',
            'shipping_city': 'Test City',
            'shipping_postal_code': '110001',
            'shipping_phone': '123',  # Invalid
        }
        
        response = self.client.post(reverse('orders:order_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid 10-digit mobile number')


class OrderHistoryViewTest(TestCase):
    """Test Order History View"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD123',
            shipping_address='Test',
            shipping_city='Test',
            shipping_postal_code='123456',
            shipping_phone='1234567890',
            subtotal=100.00,
            total=100.00
        )
        
    def test_order_history_requires_login(self):
        """Test order history requires login"""
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 302)
        
    def test_order_history_shows_orders(self):
        """Test order history shows user's orders"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ORD123')


class OrderDetailViewTest(TestCase):
    """Test Order Detail View"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD123',
            shipping_address='Test',
            shipping_city='Test',
            shipping_postal_code='123456',
            shipping_phone='1234567890',
            subtotal=100.00,
            total=100.00
        )
        
    def test_order_detail_requires_login(self):
        """Test order detail requires login"""
        response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)
        
    def test_order_detail_requires_ownership(self):
        """Test order detail requires ownership"""
        other_user = User.objects.create_user(username='other', password='otherpass')
        self.client.login(username='other', password='otherpass')
        response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 404)
        
    def test_order_detail_shows_order(self):
        """Test order detail shows correct order"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ORD123')


class AdminDashboardViewTest(TestCase):
    """Test Admin Dashboard View"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create some orders
        for i in range(5):
            Order.objects.create(
                user=self.user,
                order_number=f'ORD{i}',
                shipping_address='Test',
                shipping_city='Test',
                shipping_postal_code='123456',
                shipping_phone='1234567890',
                subtotal=100.00,
                total=100.00,
                status='pending' if i % 2 == 0 else 'payment_pending'
            )
            
    def test_admin_dashboard_requires_staff(self):
        """Test admin dashboard requires staff access"""
        response = self.client.get(reverse('orders:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('orders:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        
    def test_admin_dashboard_shows_stats(self):
        """Test admin dashboard shows correct stats"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('orders:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5')  # Total orders
        self.assertContains(response, '3')  # Pending orders (3 out of 5)
        self.assertContains(response, '2')  # Payment pending (2 out of 5)


class MarkOrderAsPaidViewTest(TestCase):
    """Test Mark Order As Paid View"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD123',
            shipping_address='Test',
            shipping_city='Test',
            shipping_postal_code='123456',
            shipping_phone='1234567890',
            subtotal=100.00,
            total=100.00,
            status='payment_pending',
            payment_status='pending'
        )
        
    def test_mark_as_paid_requires_login(self):
        """Test mark as paid requires login"""
        response = self.client.post(reverse('orders:mark_as_paid', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)
        
    def test_mark_as_paid_requires_ownership(self):
        """Test mark as paid requires ownership"""
        other_user = User.objects.create_user(username='other', password='otherpass')
        self.client.login(username='other', password='otherpass')
        response = self.client.post(reverse('orders:mark_as_paid', args=[self.order.id]))
        self.assertEqual(response.status_code, 404)
        
    def test_mark_as_paid_updates_order(self):
        """Test marking order as paid updates status"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('orders:mark_as_paid', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'processing')
        
    def test_mark_as_paid_already_paid(self):
        """Test marking already paid order"""
        self.order.payment_status = 'paid'
        self.order.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('orders:mark_as_paid', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Already paid')
        
    def test_mark_as_paid_invalid_method(self):
        """Test GET request to mark as paid"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('orders:mark_as_paid', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])