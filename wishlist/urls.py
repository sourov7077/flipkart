# wishlist/urls.py

from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    # ✅ পেজ ভিউ
    path('', views.wishlist_view, name='wishlist_view'),
    
    # ✅ AJAX API - পেইজ রিফ্রেশ ছাড়া কাজ করবে
    path('api/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('api/count/', views.wishlist_count_api, name='wishlist_count_api'),
    
    # ✅ পুরনো URL গুলো - কম্প্যাটিবিলিটির জন্য
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist_old'),
    path('remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
]