"""
Accounts Models — Custom User model with role-based access.
Supports: Farmer, Agricultural Officer, Admin roles.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based access control and profile fields for AgriSmart AI.
    """

    class Role(models.TextChoices):
        FARMER = 'farmer', _('কৃষক')            # Farmer
        OFFICER = 'officer', _('কৃষি কর্মকর্তা')  # Agricultural Officer
        ADMIN = 'admin', _('অ্যাডমিন')           # Admin

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FARMER,
        verbose_name=_('ভূমিকা'),  # Role
        db_index=True,
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('ফোন নম্বর'),  # Phone Number
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ঠিকানা'),  # Address
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('প্রোফাইল ছবি'),  # Profile Picture
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('জেলা'),  # District
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('ব্যবহারকারী')
        verbose_name_plural = _('ব্যবহারকারীগণ')
        indexes = [
            models.Index(fields=['role'], name='idx_user_role'),
            models.Index(fields=['phone'], name='idx_user_phone'),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_farmer(self):
        return self.role == self.Role.FARMER

    @property
    def is_officer(self):
        return self.role == self.Role.OFFICER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN
