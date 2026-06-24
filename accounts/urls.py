# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # ===== Authentication =====
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ===== Dashboard & Profile =====
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('password/change/', views.change_password_view, name='change_password'),
    
    # ===== Shipping Address =====
    path('shipping-address/', views.shipping_address_view, name='shipping_address'),
    path('shipping-address/edit/<int:id>/', views.edit_shipping_address, name='edit_shipping_address'),
    path('shipping-address/delete/<int:id>/', views.delete_shipping_address, name='delete_shipping_address'),
    path('shipping-address/default/<int:id>/', views.set_default_address, name='set_default_address'),
    
    # ❌ ফরগেট পাসওয়ার্ড রিমুভ করা হয়েছে
]