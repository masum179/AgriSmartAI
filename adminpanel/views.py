"""
Admin Panel Views — System administration for AgriSmart AI.
Manage diseases, recommendations, users, and detection logs.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import User
from detection.models import Disease, Recommendation, Detection
from messaging.models import ChatMessage
from .forms import AdminUserCreationForm


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict access to admin users only."""

    def test_func(self):
        return self.request.user.is_admin_user or self.request.user.is_superuser


class OfficerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict access to officer users only."""

    def test_func(self):
        return self.request.user.is_officer or self.request.user.is_superuser


class AdminDashboardView(AdminRequiredMixin, View):
    """Admin dashboard with system overview statistics."""

    template_name = 'adminpanel/dashboard.html'

    def get(self, request):
        context = {
            'total_users': User.objects.count(),
            'total_farmers': User.objects.filter(role=User.Role.FARMER).count(),
            'total_officers': User.objects.filter(role=User.Role.OFFICER).count(),
            'total_diseases': Disease.objects.count(),
            'total_detections': Detection.objects.count(),
            'recent_detections': Detection.objects.select_related('user', 'disease').order_by('-created_at')[:10],
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'pending_detections': Detection.objects.filter(status='pending').count(),
            'completed_detections': Detection.objects.filter(status='completed').count(),
        }
        return render(request, self.template_name, context)


class ManageUsersView(AdminRequiredMixin, View):
    """List and manage all users."""

    template_name = 'adminpanel/manage_users.html'

    def get(self, request):
        role_filter = request.GET.get('role', '')
        search_query = request.GET.get('search', '').strip()
        users = User.objects.all().order_by('-date_joined')
        
        if role_filter:
            users = users.filter(role=role_filter)
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        paginator = Paginator(users, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'users': page_obj,
            'role_filter': role_filter,
            'search_query': search_query,
            'roles': User.Role.choices,
        }
        return render(request, self.template_name, context)


class ToggleUserStatusView(AdminRequiredMixin, View):
    """Activate/deactivate a user account."""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user != request.user:  # Prevent self-deactivation
            user.is_active = not user.is_active
            user.save()
            status = 'সক্রিয়' if user.is_active else 'নিষ্ক্রিয়'
            messages.success(request, f'{user.username} {status} করা হয়েছে।')
        else:
            messages.error(request, 'নিজেকে নিষ্ক্রিয় করা যাবে না।')
        return redirect('adminpanel:manage_users')


class AddUserView(AdminRequiredMixin, View):
    """Admin view to create a new user."""
    
    template_name = 'adminpanel/add_user.html'

    def get(self, request):
        form = AdminUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'ব্যবহারকারী "{user.username}" সফলভাবে যোগ করা হয়েছে।')
            return redirect('adminpanel:manage_users')
        return render(request, self.template_name, {'form': form})


class DeleteUserView(AdminRequiredMixin, View):
    """Admin view to delete a user."""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'নিজেকে মুছে ফেলা যাবে না।')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'ব্যবহারকারী "{username}" মুছে ফেলা হয়েছে।')
        return redirect('adminpanel:manage_users')


class ManageDiseasesView(OfficerRequiredMixin, View):
    """List and manage diseases."""

    template_name = 'adminpanel/manage_diseases.html'

    def get(self, request):
        diseases = Disease.objects.all().prefetch_related('recommendations')
        context = {'diseases': diseases}
        return render(request, self.template_name, context)


class AddDiseaseView(OfficerRequiredMixin, View):
    """Add a new disease to the catalog."""

    template_name = 'adminpanel/add_disease.html'

    def get(self, request):
        edit_id = request.GET.get('edit')
        req_id = request.GET.get('req_id')
        context = {}
        if edit_id:
            disease = get_object_or_404(Disease, id=edit_id)
            context['disease'] = disease
            context['req_id'] = req_id
        return render(request, self.template_name, context)

    def post(self, request):
        name_bn = request.POST.get('name_bn', '').strip()
        name_en = request.POST.get('name_en', '').strip()
        description_bn = request.POST.get('description_bn', '').strip()
        crop_type = request.POST.get('crop_type', '').strip()
        severity = request.POST.get('severity', 'medium')

        edit_id = request.POST.get('edit_id')
        req_id = request.POST.get('req_id')

        if name_bn and name_en and crop_type:
            if edit_id:
                disease = get_object_or_404(Disease, id=edit_id)
                disease.name_bn = name_bn
                disease.name_en = name_en
                disease.description_bn = description_bn
                disease.crop_type = crop_type
                disease.severity = severity
                disease.is_active = True  # Activate pending diseases
                disease.save()
                messages.success(request, f'রোগ "{name_bn}" সফলভাবে আপডেট করা হয়েছে।')
                
                # Resolve info request if any
                if req_id:
                    from detection.models import InfoRequest
                    req = InfoRequest.objects.filter(id=req_id).first()
                    if req:
                        req.is_responded = True
                        req.save()
            else:
                disease = Disease.objects.create(
                    name_bn=name_bn,
                    name_en=name_en,
                    description_bn=description_bn,
                    crop_type=crop_type,
                    severity=severity,
                    is_active=True
                )
                messages.success(request, f'"{name_bn}" রোগ সফলভাবে যোগ করা হয়েছে!')

            # Add recommendation if provided
            treatment = request.POST.get('treatment_bn', '').strip()
            pesticide = request.POST.get('pesticide_bn', '').strip()
            pesticide_cost = request.POST.get('pesticide_cost_bn', '').strip()
            prevention = request.POST.get('prevention_bn', '').strip()

            if treatment:
                Recommendation.objects.create(
                    disease=disease,
                    treatment_bn=treatment,
                    pesticide_bn=pesticide,
                    pesticide_cost_bn=pesticide_cost,
                    prevention_bn=prevention,
                )

            return redirect('adminpanel:manage_diseases')
        else:
            messages.error(request, 'সব প্রয়োজনীয় তথ্য পূরণ করুন।')
            return render(request, self.template_name)


class DeleteDiseaseView(OfficerRequiredMixin, View):
    """Officer/Admin view to delete a disease."""

    def post(self, request, pk):
        disease = get_object_or_404(Disease, pk=pk)
        disease_name = disease.name_bn
        disease.delete()
        messages.success(request, f'"{disease_name}" রোগটি সফলভাবে মুছে ফেলা হয়েছে।')
        
        # Redirect back to referring page or manage diseases
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'adminpanel:manage_diseases'
        if next_url.startswith('/'):
            return redirect(next_url)
        return redirect('adminpanel:manage_diseases')


class ManageRecommendationsView(OfficerRequiredMixin, View):
    """List and manage recommendations."""

    template_name = 'adminpanel/manage_recommendations.html'

    def get(self, request):
        recommendations = Recommendation.objects.all().select_related('disease')
        context = {'recommendations': recommendations}
        return render(request, self.template_name, context)


class DetectionLogsView(OfficerRequiredMixin, View):
    """View all detection logs."""

    template_name = 'adminpanel/detection_logs.html'

    def get(self, request):
        detections = Detection.objects.all().select_related(
            'user', 'disease'
        ).order_by('-created_at')

        status_filter = request.GET.get('status', '')
        if status_filter:
            detections = detections.filter(status=status_filter)

        context = {
            'detections': detections,
            'status_filter': status_filter,
        }
        return render(request, self.template_name, context)


class DeleteDetectionLogView(OfficerRequiredMixin, View):
    """Admin/Officer view to delete a detection log."""

    def post(self, request, pk):
        detection = get_object_or_404(Detection, pk=pk)
        detection.delete()
        messages.success(request, 'শনাক্তকরণ লগ সফলভাবে মুছে ফেলা হয়েছে।')
        
        # Redirect back to referring page (dashboard or logs page)
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'adminpanel:detection_logs'
        if next_url.startswith('/'):
            return redirect(next_url)
        return redirect('adminpanel:detection_logs')
