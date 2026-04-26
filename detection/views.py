"""
Detection Views — Image upload, AI prediction, history, bookmarks.
Uses Class-Based Views following Django best practices.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from .models import Detection, Disease, DiseaseImage, Recommendation, InfoRequest
from .forms import ImageUploadForm
from .ai_service import mock_predict_disease
from django.contrib.auth.mixins import UserPassesTestMixin


def to_bangla_numeral(number_str):
    bn_digits = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
    return ''.join(bn_digits.get(c, c) for c in str(number_str))


class UploadView(LoginRequiredMixin, View):
    """Handle image upload for disease detection."""

    template_name = 'detection/upload.html'

    def get(self, request):
        form = ImageUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            detection = form.save(commit=False)
            detection.user = request.user
            detection.status = Detection.Status.PENDING
            detection.save()

            # Run mock AI prediction
            try:
                result = mock_predict_disease(detection.image.path)

                if result['success']:
                    # Link the predicted disease
                    disease = Disease.objects.get(id=result['disease_id'])
                    detection.disease = disease
                    detection.confidence = result['confidence']
                    detection.status = Detection.Status.COMPLETED
                    detection.result_data = result
                    detection.save()

                    messages.success(request, 'রোগ সফলভাবে শনাক্ত হয়েছে!')  # Disease detected
                    return redirect('detection:result', pk=detection.pk)
                else:
                    detection.status = Detection.Status.FAILED
                    detection.result_data = result
                    detection.save()
                    messages.error(request, result.get('error', 'শনাক্তকরণ ব্যর্থ হয়েছে।'))

            except Exception as e:
                detection.status = Detection.Status.FAILED
                detection.save()
                messages.error(request, f'ত্রুটি ঘটেছে: সিস্টেমে সমস্যা হয়েছে।')  # Error occurred

            return redirect('detection:upload')

        return render(request, self.template_name, {'form': form})


class ResultView(LoginRequiredMixin, View):
    """Display detection result with disease info and recommendations."""

    template_name = 'detection/result.html'

    def get(self, request, pk):
        detection = get_object_or_404(Detection, pk=pk, user=request.user)
        recommendations = []
        gallery_images = []
        if detection.disease:
            recommendations = detection.disease.recommendations.filter(is_active=True)
            gallery_images = detection.disease.images.filter(is_gallery=True)

        confidence_bn = to_bangla_numeral(f"{detection.confidence * 100:.0f}")

        context = {
            'detection': detection,
            'recommendations': recommendations,
            'gallery_images': gallery_images,
            'confidence_bn': confidence_bn,
        }
        return render(request, self.template_name, context)


class HistoryView(LoginRequiredMixin, View):
    """Display user's detection history with filtering."""

    template_name = 'detection/history.html'

    def get(self, request):
        detections = Detection.objects.filter(
            user=request.user
        ).select_related('disease').order_by('-created_at')

        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            detections = detections.filter(status=status_filter)

        # Filter bookmarked only
        bookmarked = request.GET.get('bookmarked', '')
        if bookmarked == '1':
            detections = detections.filter(is_bookmarked=True)

        context = {
            'detections': detections,
            'status_filter': status_filter,
            'bookmarked': bookmarked,
        }
        return render(request, self.template_name, context)


class ToggleBookmarkView(LoginRequiredMixin, View):
    """Toggle bookmark status for a detection."""

    def post(self, request, pk):
        detection = get_object_or_404(Detection, pk=pk, user=request.user)
        detection.is_bookmarked = not detection.is_bookmarked
        detection.save()

        if detection.is_bookmarked:
            messages.success(request, 'বুকমার্ক করা হয়েছে!')  # Bookmarked
        else:
            messages.info(request, 'বুকমার্ক সরানো হয়েছে।')  # Bookmark removed

        # Return JSON for AJAX or redirect
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'bookmarked': detection.is_bookmarked,
                'message': 'বুকমার্ক আপডেট হয়েছে।',
            })
        return redirect('detection:history')


class RequestInfoView(LoginRequiredMixin, View):
    """Handle farmer requests for more information on an unverified disease."""

    def post(self, request, disease_id):
        disease = get_object_or_404(Disease, id=disease_id)
        
        # Don't create duplicate pending requests for the same disease by the same user
        request_obj, created = InfoRequest.objects.get_or_create(
            user=request.user,
            disease=disease,
            is_responded=False,
            defaults={'message': 'কৃষক এই রোগ সম্পর্কে আরও তথ্য জানতে চান।'}
        )
        
        if created:
            messages.success(request, 'আপনার অনুরোধটি কৃষি কর্মকর্তার কাছে সফলভাবে পাঠানো হয়েছে।')
        else:
            messages.info(request, 'আপনি ইতিমধ্যেই এই রোগ সম্পর্কে তথ্যের জন্য অনুরোধ করেছেন।')
            
        return redirect(request.META.get('HTTP_REFERER', 'detection:history'))


class BookmarkListView(LoginRequiredMixin, View):
    """List bookmarked detections."""

    template_name = 'detection/bookmarks.html'

    def get(self, request):
        detections = Detection.objects.filter(
            user=request.user, is_bookmarked=True
        ).select_related('disease').order_by('-created_at')

        return render(request, self.template_name, {'detections': detections})


class DiseaseListView(LoginRequiredMixin, View):
    """View all diseases in the catalog. Officers and Admins only."""

    template_name = 'detection/disease_list.html'

    def get(self, request):
        # Farmers cannot access this page
        if request.user.is_farmer:
            messages.error(request, 'এই পৃষ্ঠাটি শুধুমাত্র কৃষি কর্মকর্তাদের জন্য।')
            return redirect('accounts:farmer_dashboard')

        diseases = Disease.objects.filter(is_active=True).prefetch_related('recommendations')

        # Chart data
        from django.db.models import Count
        crop_stats = list(Disease.objects.filter(is_active=True).values('crop_type').annotate(count=Count('id')).order_by('-count'))
        severity_stats = list(Disease.objects.filter(is_active=True).values('severity').annotate(count=Count('id')))

        context = {
            'diseases': diseases,
            'crop_stats': crop_stats,
            'severity_stats': severity_stats,
        }
        return render(request, self.template_name, context)


class OfficerOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allow access to Agricultural Officers and Admins."""

    def test_func(self):
        user = self.request.user
        return user.is_officer or user.is_admin_user or user.is_superuser


class OfficerAddDiseaseView(OfficerOrAdminMixin, View):
    """Officers and Admins can add new diseases to the catalog."""

    template_name = 'detection/officer_add_disease.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name_bn = request.POST.get('name_bn', '').strip()
        name_en = request.POST.get('name_en', '').strip()
        description_bn = request.POST.get('description_bn', '').strip()
        crop_type = request.POST.get('crop_type', '').strip()
        severity = request.POST.get('severity', 'medium')

        if not (name_bn and name_en and crop_type):
            messages.error(request, 'সব প্রয়োজনীয় তথ্য পূরণ করুন।')
            return render(request, self.template_name)

        disease = Disease.objects.create(
            name_bn=name_bn,
            name_en=name_en,
            description_bn=description_bn,
            crop_type=crop_type,
            severity=severity,
        )

        # Optional recommendation
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

        messages.success(request, f'"রোগ {name_bn}" সফলভাবে যোগ করা হয়েছে!')
        return redirect('detection:disease_list')


class DeleteDetectionView(LoginRequiredMixin, View):
    """Allow users to delete their own detections."""
    
    def post(self, request, pk):
        detection = get_object_or_404(Detection, pk=pk, user=request.user)
        detection.delete()
        messages.success(request, 'সনাক্তকরণ সফলভাবে মুছে ফেলা হয়েছে।')  # Detection deleted successfully
        
        # Redirect back to where they came from
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'detection:history'
        if next_url.startswith('/'):
            return redirect(next_url)
        return redirect('detection:history')
