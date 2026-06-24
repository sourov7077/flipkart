# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError

from .forms import RegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm, ShippingAddressForm
from .models import UserProfile, ShippingAddress
import base64
from PIL import Image
import io
import re


def get_image_format(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        img.verify()
        return img.format.lower() if img.format else None
    except:
        return None


# ============================================================
# ✅ REGISTER - সাকসেস মেসেজ + লগইন পেজে রিডাইরেক্ট
# ============================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, '✅ Account created successfully! Please login.')
                return redirect('accounts:login')
                
            except IntegrityError as e:
                if 'email' in str(e) or 'username' in str(e):
                    messages.error(request, '❌ This email is already registered.')
                else:
                    messages.error(request, '❌ Something went wrong. Please try again.')
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
        else:
            # ফর্ম এরর গুলো লুপ করে মেসেজে পুশ করা
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


# ============================================================
# ✅ LOGIN - ইমেইল + পাসওয়ার্ড (ফর্ম ভ্যালিডেশন ফিক্সড)
# ============================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            if user is not None:
                login(request, user)
                messages.success(request, f'✅ Welcome back, {user.first_name or user.username}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '✅ You have been logged out successfully.')
    return redirect('home:home')


@login_required
def dashboard_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    
    recent_orders = []
    try:
        from orders.models import Order
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    except:
        pass
    
    context = {
        'profile': user_profile,
        'shipping_addresses': shipping_addresses,
        'recent_orders': recent_orders,
        'orders': {'count': len(recent_orders)},
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_update_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user_form.save()
                
                user_profile.phone = profile_form.cleaned_data.get('phone', '')
                user_profile.address = profile_form.cleaned_data.get('address', '')
                user_profile.city = profile_form.cleaned_data.get('city', '')
                user_profile.postal_code = profile_form.cleaned_data.get('postal_code', '')
                
                if profile_form.cleaned_data.get('remove_picture'):
                    user_profile.profile_picture_base64 = None
                    user_profile.profile_picture_format = None
                
                if 'profile_picture' in request.FILES:
                    image_file = request.FILES['profile_picture']
                    try:
                        image_data = image_file.read()
                        image_format = get_image_format(image_data)
                        
                        if image_format:
                            image_file.seek(0)
                            base64_str = base64.b64encode(image_data).decode('utf-8')
                            user_profile.profile_picture_base64 = base64_str
                            user_profile.profile_picture_format = image_format
                            messages.success(request, '✅ Profile picture uploaded successfully!')
                        else:
                            messages.error(request, '❌ Invalid image format. Please upload JPG, PNG or GIF.')
                    except Exception as e:
                        messages.error(request, f'❌ Error uploading image: {str(e)}')
                
                user_profile.save()
                messages.success(request, '✅ Profile updated successfully!')
                return redirect('accounts:dashboard')
                
            except Exception as e:
                messages.error(request, f'❌ Error updating profile: {str(e)}')
        else:
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'has_picture': bool(user_profile.profile_picture_base64)
    }
    return render(request, 'accounts/profile_update.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, '✅ Password changed successfully!')
                return redirect('accounts:dashboard')
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def shipping_address_view(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            try:
                address = form.save(commit=False)
                address.user = request.user
                
                if address.is_default:
                    ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
                
                address.save()
                messages.success(request, '✅ Shipping address added successfully!')
                return redirect('accounts:shipping_address')
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = ShippingAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form
    }
    return render(request, 'accounts/shipping_address.html', context)


@login_required
def edit_shipping_address(request, id):
    address = get_object_or_404(ShippingAddress, id=id, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            try:
                address = form.save(commit=False)
                if address.is_default:
                    ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
                address.save()
                messages.success(request, '✅ Shipping address updated successfully!')
                return redirect('accounts:shipping_address')
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = ShippingAddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address
    }
    return render(request, 'accounts/edit_shipping_address.html', context)


@login_required
def delete_shipping_address(request, id):
    address = get_object_or_404(ShippingAddress, id=id, user=request.user)
    try:
        address.delete()
        messages.success(request, '✅ Shipping address deleted successfully!')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('accounts:shipping_address')


@login_required
def set_default_address(request, id):
    if request.method == 'POST':
        address = get_object_or_404(ShippingAddress, id=id, user=request.user)
        try:
            ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
            address.save()
            messages.success(request, '✅ Default address updated!')
            return redirect('accounts:shipping_address')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
    return redirect('accounts:shipping_address')