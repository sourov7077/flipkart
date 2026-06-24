# products/management/commands/import_products.py
from django.core.management.base import BaseCommand
from products.models import Product
from home.models import Category
from products.models import Brand
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import 29 products from product.html file into Home & Electronics categories (Reversed Order)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔄 Starting product import (REVERSED ORDER)...'))

        # ✅ ইতিমধ্যে থাকা ক্যাটাগরি খুঁজুন
        try:
            home_category = Category.objects.get(name='Home')
            electronics_category = Category.objects.get(name='Electronics')
            self.stdout.write(f'✅ Found categories: Home, Electronics')
        except Category.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'❌ Category not found! Please create "Home" and "Electronics" categories first.'))
            return

        # ✅ Brand খুঁজুন (ইতিমধ্যে তৈরি আছে)
        brand_names = [
            'Atomberg', 'GREEN SOUL', 'Crompton', 'Butterfly', 'BAJAJ',
            'Pigeon', 'V-Guard', 'Samsung', 'MILTON', 'SONY',
            'Prestige', 'Wildcraft', 'Turbo', 'Flipkart SmartBuy',
            'Sowbaghya', 'Snapple', 'Safari', 'Realme', 'Kanishka',
            'MGKENTERPRISE', 'Longway', 'JKR Enterprise', 'NYTK RETAIL',
            'THUNDERFIT', 'Owme'
        ]
        
        brand_map = {}
        for name in brand_names:
            brand, _ = Brand.objects.get_or_create(name=name)
            brand_map[name] = brand
        self.stdout.write(f'✅ {len(brand_map)} brands ready')

        # ✅ প্রোডাক্ট ডাটা (আপনার product.html ফাইল থেকে - উল্টো ক্রমে)
        products_data = [
            # ========== ২৯. Owme Portable USB Rechargeable Juicer (শেষ → প্রথম) ==========
            {
                'name': 'Owme Portable USB Rechargeable Juicer',
                'brand': 'Owme',
                'category': 'Home',
                'price': 249.00,
                'old_price': 999.00,
                'description': 'Make fresh juices on the go with the Owme Portable USB Rechargeable Juicer. This 105-watt mini blender is perfect for smoothies, shakes, and fresh fruit juices. The portable handheld design with a 1-jar capacity makes it ideal for office, gym, and travel. Simply charge via USB and enjoy delicious, healthy drinks anywhere. The blue color adds a pop of style to your lifestyle. Stay healthy, stay refreshed – Owme juices for life!',
                'stock': 50,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২৮. THUNDERFIT 3-Piece Stainless Steel Knife Set ==========
            {
                'name': 'THUNDERFIT 3-Piece Stainless Steel Knife Set',
                'brand': 'THUNDERFIT',
                'category': 'Home',
                'price': 298.00,
                'old_price': 799.00,
                'description': 'Equip your kitchen with the THUNDERFIT 3-Piece Stainless Steel Knife Set. This professional-quality set includes knives designed for butchering, meat preparation, paring, and vegetable cutting. The ultra-sharp stainless steel blades ensure precision cutting, while the printed SS handles provide a secure, comfortable grip. Durable, rust-resistant, and easy to maintain – this knife set is a must-have for every home chef.',
                'stock': 40,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২৭. NYTK RETAIL 2025 Foldable Barbeque Grill ==========
            {
                'name': 'NYTK RETAIL 2025 Foldable Barbeque Grill',
                'brand': 'NYTK RETAIL',
                'category': 'Home',
                'price': 489.00,
                'old_price': 999.00,
                'description': 'Host the perfect backyard party with the NYTK RETAIL 2025 Foldable Barbeque Grill. This complete barbeque set includes 2 spatulas, 1 BBQ grill, 10 skewer sticks, and 1 air blower for hassle-free grilling. The foldable design makes it easy to store and transport, while the charcoal grill delivers authentic smoky flavor to your food. Perfect for camping, picnics, and home parties – enjoy delicious grilled food anytime, anywhere!',
                'stock': 20,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২৬. JKR Enterprise 260W Hand Blender ==========
            {
                'name': 'JKR Enterprise 260W Hand Blender',
                'brand': 'JKR Enterprise',
                'category': 'Home',
                'price': 199.00,
                'old_price': 599.00,
                'description': 'Blend, whisk, and mix with the JKR Enterprise 260W Hand Blender. This powerful 260-watt blender features 7-speed settings for versatile food preparation – from pureeing soups to whipping cream. The white design looks clean and modern, while the ergonomic handle ensures comfortable use. The detachable blending shaft makes cleaning quick and easy. Compact and powerful, it\'s perfect for small kitchens and quick meal prep.',
                'stock': 45,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২৫. Longway Digital Kitchen Weighing Scale ==========
            {
                'name': 'Longway Digital Kitchen Weighing Scale',
                'brand': 'Longway',
                'category': 'Home',
                'price': 149.00,
                'old_price': 399.00,
                'description': 'Perfect your recipes with the Longway Multipurpose Digital Kitchen Scale. This portable weighing scale delivers accurate measurements for all your cooking and baking needs. The sleek gray design looks stylish on any kitchen counter, while the easy-to-read display ensures precise results every time. Whether you\'re measuring ingredients for a cake or portioning meals, this digital scale is your go-to kitchen companion. Cook with confidence, measure with precision.',
                'stock': 60,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২৪. MGKENTERPRISE 4-Layer Kitchen Storage Rack ==========
            {
                'name': 'MGKENTERPRISE 4-Layer Kitchen Storage Rack',
                'brand': 'MGKENTERPRISE',
                'category': 'Home',
                'price': 397.00,
                'old_price': 799.00,
                'description': 'Organize your kitchen efficiently with the MGKENTERPRISE 4-Layer Kitchen Rack. This versatile rack is perfect for storing fruits, vegetables, and pantry essentials. The 4-tier design maximizes vertical space, while the plastic and steel construction ensures durability. The modern trolly design with wheels makes it easy to move around the kitchen. Keep your kitchen clutter-free and stylish with this practical storage solution.',
                'stock': 35,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২৩. Pigeon Electric Kettle 1.2L ==========
            {
                'name': 'Pigeon Electric Kettle 1.2L',
                'brand': 'Pigeon',
                'category': 'Home',
                'price': 299.00,
                'old_price': 999.00,
                'description': 'Boil water in minutes with the Pigeon Electric Kettle. This 1.2-liter kettle features a stylish silver and black design that looks great on any countertop. The rapid boiling technology saves time and energy, while the auto shut-off function ensures safety. The comfortable handle and easy-pour spout make daily use convenient and spill-free. Perfect for tea, coffee, oatmeal, and more – your quick-boiling companion is here!',
                'stock': 50,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২২. Flipkart SmartBuy 40-Piece Melamine Dinner Set ==========
            {
                'name': 'Flipkart SmartBuy 40-Piece Melamine Dinner Set',
                'brand': 'Flipkart SmartBuy',
                'category': 'Home',
                'price': 469.00,
                'old_price': 1399.00,
                'description': 'Elevate your dining experience with the Flipkart SmartBuy 40-Piece Melamine Dinner Set. This Emerald Bloom collection features dishwasher-safe, stain-resistant dinnerware that\'s perfect for everyday use. The white and green floral design adds a fresh, elegant touch to your table. With 40 pieces, this set is ideal for large families and special occasions. Durable, lightweight, and beautiful – make every meal a celebration!',
                'stock': 40,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২১. Kanishka Premium Ceiling Fan (Pack of 2) ==========
            {
                'name': 'Kanishka Premium Ceiling Fan (Pack of 2)',
                'brand': 'Kanishka',
                'category': 'Home',
                'price': 549.00,
                'old_price': 2499.00,
                'description': 'Keep your home cool and comfortable with the Kanishka Premium Ceiling Fan. This pack includes 2 fans with a 1200mm sweep, perfect for medium to large rooms. The energy-saving technology helps reduce electricity bills while the anti-dust and anti-rust coating ensures long-lasting performance. The ultra-high-speed motor delivers powerful air circulation, while the smoke brown finish adds a touch of elegance to any interior. Reliable, efficient, and stylish – Kanishka fans are built to last.',
                'stock': 30,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২০. Realme TechLife 7.5kg Washing Machine (Electronics) ==========
            {
                'name': 'Realme TechLife 7.5kg Washing Machine',
                'brand': 'Realme',
                'category': 'Electronics',
                'price': 2999.00,
                'old_price': 7790.00,
                'description': 'Upgrade your laundry routine with the Realme TechLife 7.5kg Semi-Automatic Washing Machine. This 5-star rated machine delivers powerful cleaning performance with energy efficiency. The top-load design makes loading and unloading effortless, while the 7.5kg capacity handles family-sized loads with ease. The stylish black & grey design adds a modern touch to your utility room. Trust Realme\'s technology for clean, fresh clothes every day.',
                'stock': 15,
                'is_active': True,
                'is_featured': True
            },
            # ========== ১৯. Safari Magnum Fury 3-Piece Luggage Set ==========
            {
                'name': 'Safari Magnum Fury 3-Piece Luggage Set',
                'brand': 'Safari',
                'category': 'Home',
                'price': 499.00,
                'old_price': 3999.00,
                'description': 'Travel like a pro with the Safari Magnum Fury 3-Piece Luggage Set. This set includes small (55cm), medium (65cm), and large (75cm) suitcases – perfect for trips of all lengths. The hard body construction provides excellent protection, while the 4 smooth wheels ensure effortless navigation. The vibrant blue color makes your luggage easy to spot on the carousel. Durable, stylish, and reliable – Safari luggage is your perfect travel companion.',
                'stock': 25,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১৮. Snapple TAG Stainless Steel Water Bottle (Pack of 6) ==========
            {
                'name': 'Snapple TAG Stainless Steel Water Bottle (Pack of 6)',
                'brand': 'Snapple',
                'category': 'Home',
                'price': 649.00,
                'old_price': 1199.00,
                'description': 'Stay hydrated throughout the day with the Snapple TAG Stainless Steel Water Bottle. This 1000ml bottle features single-wall construction with ISI certification for quality assurance. The pack includes 6 bottles – perfect for the whole family. The sleek silver design looks stylish while the durable steel construction ensures long-lasting use. Ideal for home, office, gym, and outdoor activities. Drink healthy, drink from Snapple!',
                'stock': 30,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১৭. Sowbaghya 26-Piece Steel Dinner Set ==========
            {
                'name': 'Sowbaghya 26-Piece Steel Dinner Set',
                'brand': 'Sowbaghya',
                'category': 'Home',
                'price': 1299.00,
                'old_price': 2299.00,
                'description': 'Serve your family in style with the Sowbaghya 26-Piece Steel Dinner Set. This premium-quality stainless steel set includes everything you need for a complete dining experience – dinner plates, bowls, and serving dishes. The mirror-polished silver finish adds elegance to any dining table. Durable, rust-resistant, and easy to clean, this set is perfect for everyday use. Make every meal special with Sowbaghya\'s timeless dinnerware collection.',
                'stock': 20,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১৬. Flipkart SmartBuy 20-Piece Plastic Container Set ==========
            {
                'name': 'Flipkart SmartBuy 20-Piece Plastic Container Set',
                'brand': 'Flipkart SmartBuy',
                'category': 'Home',
                'price': 197.00,
                'old_price': 401.00,
                'description': 'Keep your kitchen organized with the Flipkart SmartBuy 20-Piece Plastic Container Set. This versatile set includes containers in multiple sizes – 1200ml, 650ml, 350ml, and 250ml – perfect for storing groceries, leftovers, and snacks. Made from food-grade, BPA-free plastic, these containers are safe for your family. The transparent design allows you to see the contents easily, while the secure lids keep food fresh longer. Kitchen organization made simple and affordable!',
                'stock': 60,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১৫. Prestige Festival Pack Cookware Set ==========
            {
                'name': 'Prestige Festival Pack Cookware Set',
                'brand': 'Prestige',
                'category': 'Home',
                'price': 398.00,
                'old_price': 1699.00,
                'description': 'Build your dream kitchen with the Prestige Festival Pack Cookware Set. This 3-piece aluminium cookware set features induction-compatible bases and premium non-stick coating for healthy, oil-free cooking. The set includes everything you need to get started – from frying pans to saucepans. The ergonomic handles ensure comfortable grip, while the durable construction guarantees years of reliable use. Perfect for beginners and experienced cooks alike.',
                'stock': 35,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১৪. Turbo Heavy Duty Outdoor Chair (Set of 4) ==========
            {
                'name': 'Turbo Heavy Duty Outdoor Chair (Set of 4)',
                'brand': 'Turbo',
                'category': 'Home',
                'price': 497.00,
                'old_price': 2999.00,
                'description': 'Make your outdoor spaces comfortable with the Turbo Heavy Duty Plastic Chair Set. This set includes 4 super-strong, weather-resistant chairs perfect for gardens, balconies, and dining areas. The feather brown finish adds a warm, natural look to any setting. Made from premium-quality polypropylene, these chairs offer excellent durability and stability. Lightweight and stackable, they\'re easy to store when not in use. Ideal for homes, restaurants, and events.',
                'stock': 25,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১৩. Wildcraft TorQ Medium Check-in Suitcase ==========
            {
                'name': 'Wildcraft TorQ Medium Check-in Suitcase',
                'brand': 'Wildcraft',
                'category': 'Home',
                'price': 399.00,
                'old_price': 1999.00,
                'description': 'Travel in style with the Wildcraft TorQ Medium Check-in Suitcase. This 67cm suitcase features 4 smooth-rolling wheels for effortless maneuverability. Made from premium-quality materials, it offers excellent durability and protection for your belongings. The spacious interior with compression straps keeps your clothes organized during travel. Whether for business or leisure, this Wildcraft suitcase combines functionality with contemporary design.',
                'stock': 40,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১২. Prestige Nutrifry Digital Air Fryer ==========
            {
                'name': 'Prestige Nutrifry Digital Air Fryer',
                'brand': 'Prestige',
                'category': 'Home',
                'price': 1599.00,
                'old_price': 3498.00,
                'description': 'Enjoy guilt-free fried food with the Prestige Nutrifry Digital Air Fryer. This 4.5-liter air fryer uses rapid air circulation technology to fry your favorite snacks with up to 85% less oil. The digital control panel allows precise temperature and time settings for perfect results every time. Cook crispy fries, chicken wings, vegetables, and even desserts – all with just a touch of oil. Healthy eating has never been this delicious and easy!',
                'stock': 30,
                'is_active': True,
                'is_featured': False
            },
            # ========== ১১. Sony SA-D40M2 Home Theatre System (Electronics) ==========
            {
                'name': 'Sony SA-D40M2 Home Theatre System',
                'brand': 'SONY',
                'category': 'Electronics',
                'price': 499.00,
                'old_price': 9490.00,
                'description': 'Transform your living room into a cinema with the Sony SA-D40M2 4.1ch Home Theatre System. This all-in-one system delivers powerful 100W sound with a dedicated subwoofer for deep, thumping bass. Connect wirelessly via Bluetooth and enjoy your favorite music, movies, and games with crystal-clear audio. The sleek black design complements any TV setup, while the multiple input options make it versatile for all your devices. Sony\'s legendary sound quality brings every beat to life.',
                'stock': 15,
                'is_active': True,
                'is_featured': True
            },
            # ========== ১০. Bajaj Aluminium Pressure Cooker ==========
            {
                'name': 'Bajaj Aluminium Pressure Cooker',
                'brand': 'BAJAJ',
                'category': 'Home',
                'price': 399.00,
                'old_price': 1799.00,
                'description': 'Cook your favorite meals faster and healthier with the Bajaj Aluminium Pressure Cooker. Built with premium-quality aluminium, this pressure cooker offers excellent heat conductivity for even cooking. Available in 2L, 3L, and 5L sizes, it\'s perfect for small to large families. The sturdy pressure regulator ensures safety, while the comfortable handles make handling easy. Lightweight and durable, it\'s a must-have kitchen essential for everyday use.',
                'stock': 55,
                'is_active': True,
                'is_featured': False
            },
            # ========== ৯. Milton Go Electric Kettle & Flask Combo ==========
            {
                'name': 'Milton Go Electric Kettle & Flask Combo',
                'brand': 'MILTON',
                'category': 'Home',
                'price': 397.00,
                'old_price': 1699.00,
                'description': 'Stay hydrated with the Milton Go Electric Kettle & Flask Combo – the perfect travel companion for your daily needs. This combo includes a 2-liter stainless steel electric kettle and a 750ml steel flask. The kettle boils water in minutes, while the insulated flask keeps your beverages hot or cold for hours. The flip lid design ensures easy pouring and spill-free use. Whether at home, office, or on the go, this Milton combo is designed for convenience and durability.',
                'stock': 50,
                'is_active': True,
                'is_featured': False
            },
            # ========== ৮. Samsung 23L Solo Microwave Oven (Electronics) ==========
            {
                'name': 'Samsung 23L Solo Microwave Oven',
                'brand': 'Samsung',
                'category': 'Electronics',
                'price': 799.00,
                'old_price': 6999.00,
                'description': 'Revolutionize your cooking with the Samsung 23L Solo Microwave Oven – a perfect kitchen companion for fast and convenient meals. With 23-liter capacity, it\'s ideal for reheating, defrosting, and cooking delicious dishes. The Auto Cook Programs make meal preparation effortless, while Child Safety Lock ensures family safety. The memory feature allows you to save your favorite settings, and the deodorization technology keeps your microwave fresh. Sleek black design adds style to any kitchen countertop.',
                'stock': 20,
                'is_active': True,
                'is_featured': True
            },
            # ========== ৭. V-Guard VRC 1.8C Electric Rice Cooker ==========
            {
                'name': 'V-Guard VRC 1.8C Electric Rice Cooker',
                'brand': 'V-Guard',
                'category': 'Home',
                'price': 498.00,
                'old_price': 2499.00,
                'description': 'Enjoy perfectly cooked rice every time with the V-Guard VRC 1.8C Electric Rice Cooker. This 1.8-liter cooker comes with two convenient pots for versatile cooking – perfect for rice, pasta, soups, and more. The floral pattern design adds a touch of elegance to your kitchen. With auto-keep-warm function and even heat distribution, your food stays fresh for hours. Trust V-Guard\'s reliable technology for consistent performance every day.',
                'stock': 45,
                'is_active': True,
                'is_featured': False
            },
            # ========== ৬. Pigeon Brio 2100W Induction Cooktop ==========
            {
                'name': 'Pigeon Brio 2100W Induction Cooktop',
                'brand': 'Pigeon',
                'category': 'Home',
                'price': 449.00,
                'old_price': 2228.00,
                'description': 'Elevate your cooking experience with the Pigeon Brio 2100W Induction Cooktop. This sleek, modern cooktop features advanced technology for faster, safer, and more efficient cooking. The anti-magnetic wall protection ensures zero radiation hazards, making it safe for sensitive devices like pacemakers. With 2100W of power, precise temperature control, and a stylish silver-black finish, the Brio induction cooktop is perfect for modern kitchens. Cook healthy meals without any gas fumes or heat loss.',
                'stock': 35,
                'is_active': True,
                'is_featured': False
            },
            # ========== ৫. Bajaj Premium 35L Tower Air Cooler ==========
            {
                'name': 'Bajaj Premium 35L Tower Air Cooler',
                'brand': 'BAJAJ',
                'category': 'Home',
                'price': 699.00,
                'old_price': 2999.00,
                'description': 'Beat the summer heat with the Bajaj Premium 35L Tower Air Cooler – a perfect blend of style and performance. Its sleek tower design saves floor space while delivering powerful cooling for medium to large rooms. The 35-liter water tank ensures longer cooling hours, while the honeycomb cooling pads provide efficient air circulation. With 3-speed settings and smooth castor wheels, this cooler offers both convenience and comfort. Stay cool all summer long with Bajaj\'s trusted quality.',
                'stock': 25,
                'is_active': True,
                'is_featured': False
            },
            # ========== ৪. Butterfly Aluminium Pressure Cooker ==========
            {
                'name': 'Butterfly Aluminium Pressure Cooker',
                'brand': 'Butterfly',
                'category': 'Home',
                'price': 549.00,
                'old_price': 1827.00,
                'description': 'Cook healthy and delicious meals faster with the Butterfly Aluminium Pressure Cooker. Made from high-quality aluminium, this cooker ensures even heat distribution for perfectly cooked food every time. Available in 2L, 3L, and 5L sizes to suit every family\'s needs. The outer lid design and sturdy handles provide safe and easy handling. Lightweight yet durable, it\'s the perfect addition to your kitchen for daily cooking.',
                'stock': 60,
                'is_active': True,
                'is_featured': False
            },
            # ========== ৩. Crompton DS 500W Mixer Grinder ==========
            {
                'name': 'Crompton DS 500W Mixer Grinder',
                'brand': 'Crompton',
                'category': 'Home',
                'price': 597.00,
                'old_price': 1799.00,
                'description': 'Upgrade your kitchen with the Crompton DS 500W Mixer Grinder – your perfect companion for daily cooking needs. This powerful 500-watt motor effortlessly grinds spices, makes chutneys, and blends batters with ease. Comes with 3 durable jars designed for wet and dry grinding. The sleek black & grey design adds a modern touch to your countertop. With Crompton\'s trusted quality, this mixer grinder delivers consistent performance and long-lasting durability.',
                'stock': 40,
                'is_active': True,
                'is_featured': False
            },
            # ========== ২. GREEN SOUL Kiev Orthopedic Office Chair ==========
            {
                'name': 'GREEN SOUL Kiev Orthopedic Office Chair',
                'brand': 'GREEN SOUL',
                'category': 'Home',
                'price': 467.00,
                'old_price': 7190.00,
                'description': 'Experience ultimate comfort with the GREEN SOUL Kiev Orthopedic Office Chair – designed for long hours of work. Featuring an ergonomic design with rocking function, this chair provides superior lumbar support to reduce back pain. The premium leatherette upholstery adds a touch of elegance, while the adjustable armrests ensure personalized comfort. Perfect for home offices and corporate setups, this DIY chair is easy to assemble and built to last.',
                'stock': 30,
                'is_active': True,
                'is_featured': True
            },
            # ========== ১. Atomberg Renesa Prime Ceiling Fan (শেষ → প্রথম) ==========
            {
                'name': 'Atomberg Renesa Prime Ceiling Fan',
                'brand': 'Atomberg',
                'category': 'Home',
                'price': 419.00,
                'old_price': 2599.00,
                'description': 'Introducing the Atomberg Renesa Prime – India\'s most energy-efficient ceiling fan with a powerful BLDC motor. This 1200mm fan comes with a sleek remote control for effortless operation. With its 5-star energy rating, it saves up to ₹2,000 annually on electricity bills. The anti-dust and anti-rust coating ensures durability, while the silent operation makes it perfect for bedrooms and living rooms. Backed by a 5-year warranty, this fan combines style, performance, and savings like never before.',
                'stock': 50,
                'is_active': True,
                'is_featured': True
            }
        ]

        # ✅ প্রোডাক্ট Import করুন
        imported_count = 0
        skipped_count = 0

        for data in products_data:
            brand_name = data.pop('brand')
            category_name = data.pop('category')
            
            brand = brand_map.get(brand_name)
            if not brand:
                self.stdout.write(self.style.ERROR(f'❌ Brand "{brand_name}" not found!'))
                skipped_count += 1
                continue

            # ✅ ক্যাটাগরি সেট করুন
            if category_name == 'Home':
                category = home_category
            elif category_name == 'Electronics':
                category = electronics_category
            else:
                self.stdout.write(self.style.ERROR(f'❌ Invalid category "{category_name}"'))
                skipped_count += 1
                continue

            # ✅ চেক করুন প্রোডাক্ট ইতিমধ্যে আছে কিনা
            if Product.objects.filter(name=data['name']).exists():
                self.stdout.write(self.style.WARNING(f'⚠️ Skipping existing product: {data["name"]}'))
                skipped_count += 1
                continue

            # ✅ প্রোডাক্ট তৈরি করুন
            try:
                product = Product.objects.create(
                    category=category,
                    brand=brand,
                    **data
                )
                imported_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Imported: {product.name} → {category.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error importing {data["name"]}: {e}'))
                skipped_count += 1

        # ✅ Final Report
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Import complete!'))
        self.stdout.write(self.style.SUCCESS(f'📦 Imported: {imported_count} products'))
        self.stdout.write(self.style.WARNING(f'⚠️ Skipped: {skipped_count} products'))