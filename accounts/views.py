"""
Accounts Views — Authentication, registration, dashboard routing.
Uses Class-Based Views as per architecture requirements.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User
from detection.models import Detection


class RegisterView(View):
    """Handle user registration with role selection."""

    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!')  # Account created successfully
            return redirect('accounts:dashboard')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """Handle user login with role-based redirection."""

    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'স্বাগতম, {user.get_full_name() or user.username}!')
            return redirect('accounts:dashboard')
        messages.error(request, 'ভুল ব্যবহারকারীর নাম অথবা পাসওয়ার্ড।')  # Wrong credentials
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """Handle user logout."""

    def get(self, request):
        logout(request)
        messages.info(request, 'সফলভাবে লগ আউট হয়েছে।')  # Logged out
        return redirect('accounts:login')


class DashboardView(LoginRequiredMixin, View):
    """
    Role-based dashboard routing.
    Redirects to appropriate dashboard based on user role.
    """

    def get(self, request):
        user = request.user

        if user.is_admin_user:
            return redirect('adminpanel:dashboard')
        elif user.is_officer:
            return redirect('accounts:officer_dashboard')
        else:
            return redirect('accounts:farmer_dashboard')


class FarmerDashboardView(LoginRequiredMixin, View):
    """Farmer dashboard showing recent detections and quick actions."""

    template_name = 'accounts/farmer_dashboard.html'

    def get(self, request):
        from messaging.models import ChatMessage

        recent_detections = Detection.objects.filter(
            user=request.user
        ).select_related('disease').order_by('-created_at')[:5]

        total_detections = Detection.objects.filter(user=request.user).count()
        bookmarked_count = Detection.objects.filter(user=request.user, is_bookmarked=True).count()
        unread_messages = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()

        context = {
            'recent_detections': recent_detections,
            'total_detections': total_detections,
            'bookmarked_count': bookmarked_count,
            'unread_messages': unread_messages,
        }
        return render(request, self.template_name, context)


class OfficerDashboardView(LoginRequiredMixin, View):
    """Agricultural Officer dashboard with farmer messages and recent activity."""

    template_name = 'accounts/officer_dashboard.html'

    def get(self, request):
        from messaging.models import ChatMessage
        from detection.models import Disease, InfoRequest

        pending_diseases = Disease.objects.filter(is_active=False).order_by('-created_at')
        info_requests = InfoRequest.objects.filter(is_responded=False).select_related('user', 'disease').order_by('-created_at')
        farmers_count = User.objects.filter(role=User.Role.FARMER).count()
        recent_detections = Detection.objects.all().select_related('user', 'disease').order_by('-created_at')[:10]
        total_detections = Detection.objects.count()
        unread_messages = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()

        context = {
            'farmers_count': farmers_count,
            'recent_detections': recent_detections,
            'pending_diseases': pending_diseases,
            'info_requests': info_requests,
            'total_detections': total_detections,
            'unread_messages': unread_messages,
        }
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    """User profile view and update."""

    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'প্রোফাইল সফলভাবে আপডেট হয়েছে!')  # Profile updated
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})


class DeleteAccountView(LoginRequiredMixin, View):
    """View to delete user account."""

    def post(self, request):
        user = request.user
        password = request.POST.get('password')
        
        if not user.check_password(password):
            messages.error(request, 'ভুল পাসওয়ার্ড।')
            return redirect('accounts:profile')
            
        user.delete()
        messages.success(request, 'আপনার অ্যাকাউন্ট সফলভাবে মুছে ফেলা হয়েছে।')
        return redirect('accounts:login')


class ToggleLanguageView(View):
    """Toggles session language between Bangla and English."""

    def get(self, request):
        current_lang = request.session.get('lang', 'bn')
        request.session['lang'] = 'en' if current_lang == 'bn' else 'bn'
        return redirect(request.META.get('HTTP_REFERER', 'accounts:dashboard'))
