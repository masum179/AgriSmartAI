"""
Accounts URL Configuration
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('farmer/', views.FarmerDashboardView.as_view(), name='farmer_dashboard'),
    path('officer/', views.OfficerDashboardView.as_view(), name='officer_dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('toggle-lang/', views.ToggleLanguageView.as_view(), name='toggle_lang'),
]
