from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Category, CategorySliderImage, UserLocation
import json
import logging

logger = logging.getLogger(__name__)


def home(request):
    try:
        from products.models import Product
    except ImportError:
        Product = None

    # ==============================
    # For You Category
    # ==============================
    for_you_category = None
    try:
        for_you_category = Category.objects.filter(
            slug='for-you',
            is_active=True
        ).first()

        if not for_you_category:
            for_you_category = Category.objects.create(
                name='For You',
                slug='for-you',
                icon='user',
                icon_color='#2874f0',
                bg_color='#e8f0fe',
                is_default=True,
                is_active=True,
                order=0
            )

    except Exception as e:
        logger.error(f"For You category error: {e}")
        for_you_category = None

    # ==============================
    # Categories (exclude For You)
    # ==============================
    categories = Category.objects.filter(is_active=True).exclude(slug='for-you')

    category_products = {}
    category_sliders = {}

    for category in categories:
        # Sliders
        try:
            slider_images = category.get_slider_images()
            category_sliders[category.slug] = slider_images
        except Exception as e:
            logger.error(f"Slider error {category.slug}: {e}")
            category_sliders[category.slug] = []

        # Products
        if Product:
            try:
                products = Product.objects.filter(
                    category_id=category.id,
                    is_active=True
                )
                category_products[category.slug] = products
            except Exception as e:
                logger.error(f"Product error {category.slug}: {e}")
                category_products[category.slug] = []
        else:
            category_products[category.slug] = []

    # ==============================
    # For You Products
    # ==============================
    for_you_products = []
    if Product:
        try:
            for_you_products = Product.objects.filter(
                is_active=True
            ).order_by('-created_at')
        except Exception as e:
            logger.error(f"For You products error: {e}")

    # ==============================
    # For You Sliders
    # ==============================
    for_you_sliders = []
    try:
        if for_you_category:
            for_you_sliders = for_you_category.get_slider_images()
    except Exception as e:
        logger.error(f"For You sliders error: {e}")

    # ==============================
    # For You Icon
    # ==============================
    for_you_icon_url = None
    try:
        if for_you_category:
            for_you_icon_url = for_you_category.get_image_url()
    except Exception as e:
        logger.error(f"For You icon error: {e}")

    # ==============================
    # User Location
    # ==============================
    user_location = None
    if request.user.is_authenticated:
        try:
            user_location = UserLocation.objects.get(user=request.user)
        except UserLocation.DoesNotExist:
            user_location = None
        except Exception as e:
            logger.error(f"User location error: {e}")

    # ==============================
    # Context
    # ==============================
    context = {
        'categories': categories,
        'category_products': category_products,
        'category_sliders': category_sliders,
        'for_you_products': for_you_products,
        'for_you_sliders': for_you_sliders,
        'for_you_icon_url': for_you_icon_url,
        'for_you_category': for_you_category,
        'user_location': user_location,
    }

    return render(request, 'home/index.html', context)


# ==============================
# SAVE LOCATION
# ==============================
@login_required
@require_POST
@csrf_exempt
def save_location(request):
    try:
        data = json.loads(request.body)

        city = data.get('city', '').strip()
        area = data.get('area', '').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not city:
            return JsonResponse({
                'success': False,
                'message': 'City name is required'
            }, status=400)

        location, created = UserLocation.objects.update_or_create(
            user=request.user,
            defaults={
                'city': city.title(),
                'area': area,
                'latitude': latitude,
                'longitude': longitude,
            }
        )

        return JsonResponse({
            'success': True,
            'message': 'Location saved successfully!',
            'city': location.city,
            'area': location.area,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)

    except Exception as e:
        logger.error(f"Save location error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Server error'
        }, status=500)


# ==============================
# GET LOCATION
# ==============================
@login_required
def get_location(request):
    try:
        location = UserLocation.objects.get(user=request.user)

        return JsonResponse({
            'success': True,
            'city': location.city,
            'area': location.area,
            'latitude': str(location.latitude) if location.latitude else None,
            'longitude': str(location.longitude) if location.longitude else None,
        })

    except UserLocation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Location not found'
        }, status=404)

    except Exception as e:
        logger.error(f"Get location error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Server error'
        }, status=500)


# ==============================
# UPDATE LOCATION FROM BROWSER
# ==============================
@login_required
@require_POST
def update_location_from_browser(request):
    try:
        data = json.loads(request.body)

        city = data.get('city', '').strip()
        area = data.get('area', '').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not city:
            city = get_city_from_ip(request)
            if not city:
                return JsonResponse({
                    'success': False,
                    'message': 'Could not detect location'
                }, status=400)

        location, created = UserLocation.objects.update_or_create(
            user=request.user,
            defaults={
                'city': city.title(),
                'area': area,
                'latitude': latitude,
                'longitude': longitude,
            }
        )

        return JsonResponse({
            'success': True,
            'message': 'Location updated!',
            'city': location.city,
            'area': location.area,
        })

    except Exception as e:
        logger.error(f"Browser location error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Server error'
        }, status=500)


# ==============================
# IP CITY DETECTION
# ==============================
def get_city_from_ip(request):
    try:
        import requests

        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        if not ip:
            ip = request.META.get('REMOTE_ADDR', '')

        response = requests.get(
            f'http://ip-api.com/json/{ip}?fields=city,regionName,country,status',
            timeout=3
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('city') or data.get('regionName') or data.get('country')

        return None

    except Exception:
        return None