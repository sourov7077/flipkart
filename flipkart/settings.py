import os
from pathlib import Path
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,flipkart.ondigitalocean.app').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://flipkart.ondigitalocean.app',
    'http://flipkart.ondigitalocean.app',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'crispy_forms',
    'crispy_bootstrap5',
    'home',
    'accounts',
    'products',
    'cart',
    'orders',
    'coupons',
    'wishlist',
    'reviews',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flipkart.urls'
WSGI_APPLICATION = 'flipkart.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_total',
            ],
        },
    },
]

# ============================================================
# 🗄️ DATABASE - লোকাল ও প্রোডাকশন একসাথে
# ============================================================
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # ✅ App Platform (Production)
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=False
        )
    }
else:
    # ✅ Local (Termux)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'flipkart_db',
            'USER': 'flipkart_user',
            'PASSWORD': 'Flipkart1234',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ============================================================
# 📁 STATIC FILES - লোকাল ও প্রোডাকশন
# ============================================================
STATIC_URL = '/static/'

# STATIC_ROOT - যেখানে collectstatic ফাইল জমা হবে
if DEBUG:
    # ✅ লোকাল ডেভেলপমেন্ট
    STATIC_ROOT = BASE_DIR / 'staticfiles'
else:
    # ✅ App Platform (Production)
    STATIC_ROOT = '/app/staticfiles/'

# STATICFILES_DIRS - যেখানে আপনার static ফোল্ডার আছে
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================
# 📁 MEDIA FILES - লোকাল ও প্রোডাকশন
# ============================================================
MEDIA_URL = '/media/'

if DEBUG:
    # ✅ লোকাল ডেভেলপমেন্ট
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    # ✅ App Platform (Production)
    MEDIA_ROOT = '/app/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home:home'
LOGOUT_REDIRECT_URL = 'home:home'
CART_SESSION_ID = 'cart'

print("=" * 50)
print("🚀 Django Running:", "PRODUCTION" if not DEBUG else "DEVELOPMENT")
print("🗄️ Database:", "PostgreSQL (Production)" if DATABASE_URL else "PostgreSQL (Local)")
print("📁 STATIC_ROOT:", STATIC_ROOT)
print("📁 MEDIA_ROOT:", MEDIA_ROOT)
print("=" * 50)