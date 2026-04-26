"""
Accounts Admin — Custom User admin configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model with role management."""

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('AgriSmart Profile', {
            'fields': ('role', 'phone', 'address', 'district', 'profile_picture'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('AgriSmart Profile', {
            'fields': ('role', 'phone', 'district'),
        }),
    )
