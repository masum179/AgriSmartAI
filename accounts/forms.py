"""
Accounts Forms — Registration and Login forms with Bangla labels.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Registration form for new users with role selection."""

    role = forms.ChoiceField(
        choices=User.Role.choices,
        label='ভূমিকা নির্বাচন করুন',  # Select Role
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_role',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone',
                  'district', 'role', 'password1', 'password2']
        labels = {
            'username': 'ব্যবহারকারীর নাম',      # Username
            'email': 'ইমেইল',                     # Email
            'first_name': 'প্রথম নাম',            # First Name
            'last_name': 'শেষ নাম',               # Last Name
            'phone': 'ফোন নম্বর',                 # Phone Number
            'district': 'জেলা',                    # District
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ব্যবহারকারীর নাম লিখুন'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ইমেইল লিখুন'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'প্রথম নাম'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'শেষ নাম'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '০১XXXXXXXXX'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'আপনার জেলা'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'পাসওয়ার্ড'
        self.fields['password2'].label = 'পাসওয়ার্ড নিশ্চিত করুন'
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'পাসওয়ার্ড লিখুন'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'পাসওয়ার্ড আবার লিখুন'})


class UserLoginForm(AuthenticationForm):
    """Login form with Bangla labels."""

    username = forms.CharField(
        label='ব্যবহারকারীর নাম',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ব্যবহারকারীর নাম লিখুন',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='পাসওয়ার্ড',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'পাসওয়ার্ড লিখুন',
        })
    )


class UserProfileForm(forms.ModelForm):
    """Profile update form."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'district', 'address', 'profile_picture']
        labels = {
            'first_name': 'প্রথম নাম',
            'last_name': 'শেষ নাম',
            'email': 'ইমেইল',
            'phone': 'ফোন নম্বর',
            'district': 'জেলা',
            'address': 'ঠিকানা',
            'profile_picture': 'প্রোফাইল ছবি',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
