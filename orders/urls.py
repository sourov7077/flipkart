from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('mark-as-paid/<int:order_id>/', views.mark_order_as_paid, name='mark_as_paid'),
]