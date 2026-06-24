from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('save-location/', views.save_location, name='save_location'),
    path('get-location/', views.get_location, name='get_location'),
    path('update-location/', views.update_location_from_browser, name='update_location_from_browser'),
]