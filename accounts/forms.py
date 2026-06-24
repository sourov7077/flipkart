# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, ShippingAddress
import re


# ============================================================
# ✅ REGISTRATION FORM - সম্পূর্ণ ফিক্সড ও বাগ-ফ্রি
# ============================================================
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address',
            'id': 'id_email'
        })
    )
    phone = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter phone number',
            'id': 'id_phone'
        })
    )
    
    class Meta:
        model = User
        # UserCreationForm এর ইন্টারনাল পাসওয়ার্ড মেকানিজম ঠিক রাখার জন্য password1/2 মেটাতে রাখা যাবে না
        fields = ['email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ username ফিল্ড সম্পূর্ণ রিমুভ করছি কারণ আমরা ইমেইল ব্যবহার করব
        if 'username' in self.fields:
            del self.fields['username']
        
        # ✅ পাসওয়ার্ড ফিল্ডের বুটস্ট্র্যাপ স্টাইল ও আইডি সেটআপ
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': 'Create a password (min 8 characters)',
                'id': 'id_password1'
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': 'Confirm your password',
                'id': 'id_password2'
            })
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('❌ Email is required.')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('❌ This email is already registered. Please login.')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('❌ Please enter a valid email address.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone = re.sub(r'[^0-9]', '', phone)
        if not phone:
            raise ValidationError('❌ Phone number is required.')
        if len(phone) < 10 or len(phone) > 15:
            raise ValidationError('❌ Please enter a valid phone number (10-15 digits).')
        return phone
    
    def save(self, commit=True):
        # ✅ জ্যাঙ্গোর অরিজিনাল ইউজার ক্রিয়েশন মেথড কল করছি (পাসওয়ার্ড হ্যাশিং এর জন্য)
        user = super().save(commit=False)
        
        email = self.cleaned_data.get('email', '').strip().lower()
        # ✅ ইউজারনেম এবং ইমেইল একই সেট করা হলো
        user.username = email
        user.email = email
        
        if commit:
            user.save()
            # ✅ ওয়ান-টু-ওয়ান প্রোফাইল সেফলি তৈরি বা গেট করা
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'phone': self.cleaned_data.get('phone')}
            )
        return user


# ============================================================
# ✅ LOGIN FORM
# ============================================================
class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address',
            'id': 'id_login_email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password',
            'id': 'id_login_password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            from django.contrib.auth import authenticate
            user = None
            
            try:
                user_obj = User.objects.get(email__iexact=email.strip())
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
            
            if user is None:
                raise ValidationError('❌ Invalid email or password.')
            
            cleaned_data['user'] = user
        
        return cleaned_data


# ============================================================
# ✅ USER UPDATE FORM
# ============================================================
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError('❌ This email is already registered to another account.')
        return email


# ============================================================
# ✅ PROFILE UPDATE FORM
# ============================================================
class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'profile_picture_input'
        })
    )
    
    remove_picture = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remove current profile picture'
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'[^0-9]', '', phone)
            if len(phone) < 10 or len(phone) > 15:
                raise ValidationError('❌ Please enter a valid phone number (10-15 digits).')
        return phone


# ============================================================
# ✅ SHIPPING ADDRESS FORM
# ============================================================
class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'phone', 'address', 'city', 'postal_code', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'[^0-9]', '', phone)
            if len(phone) < 10 or len(phone) > 15:
                raise ValidationError('❌ Please enter a valid phone number (10-15 digits).')
        return phone