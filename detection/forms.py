"""
Detection Forms — Image upload form for crop disease detection.
"""

from django import forms
import logging
from .models import Detection

logger = logging.getLogger(__name__)


class ImageUploadForm(forms.ModelForm):
    """Form for uploading leaf images for disease detection."""

    class Meta:
        model = Detection
        fields = ['image', 'notes']
        labels = {
            'image': 'পাতার ছবি আপলোড করুন',  # Upload leaf image
            'notes': 'অতিরিক্ত নোট (ঐচ্ছিক)',   # Additional notes (optional)
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control file-input',
                'accept': 'image/*',
                'capture': 'environment',  # Allows camera on mobile
                'id': 'id_image_upload',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ফসল বা লক্ষণ সম্পর্কে লিখুন...',
            }),
        }

    def clean_image(self):
        """Validate uploaded image."""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                logger.warning(f"Image upload failed: file too large ({image.size} bytes).")
                raise forms.ValidationError('ছবির আকার ১০ এমবির বেশি হতে পারবে না।')

            # Check file type
            valid_types = ['image/jpeg', 'image/png', 'image/webp']
            if image.content_type not in valid_types:
                logger.warning(f"Image upload failed: invalid format ({image.content_type}).")
                raise forms.ValidationError('ছবিটি সঠিক নয়। অনুগ্রহ করে পুনরায় চেষ্টা করুন।')
        return image
