from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    
    # AJAX APIs
    path('api/add/', views.cart_add_ajax, name='cart_add_ajax'),
    path('api/remove/', views.cart_remove_ajax, name='cart_remove_ajax'),
    path('api/update/', views.cart_update_ajax, name='cart_update_ajax'),
    path('api/count/', views.cart_count_api, name='cart_count_api'),
    
    # Non-AJAX (Redirect)
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
]