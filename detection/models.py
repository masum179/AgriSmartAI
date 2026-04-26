"""
Detection Models — Disease detection, disease catalog, recommendations.
Core data models for the AI crop disease detection system.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Disease(models.Model):
    """
    Disease catalog — stores all known crop diseases.
    Designed for admin management and AI reference.
    """
    name_bn = models.CharField(
        max_length=200,
        verbose_name=_('রোগের নাম (বাংলা)'),  # Disease Name (Bangla)
    )
    name_en = models.CharField(
        max_length=200,
        verbose_name=_('রোগের নাম (ইংরেজি)'),  # Disease Name (English)
    )
    description_bn = models.TextField(
        verbose_name=_('বিবরণ (বাংলা)'),  # Description (Bangla)
        blank=True,
    )
    crop_type = models.CharField(
        max_length=100,
        verbose_name=_('ফসলের ধরণ'),  # Crop Type
        db_index=True,
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'কম'),
            ('medium', 'মাঝারি'),
            ('high', 'উচ্চ'),
            ('critical', 'জরুরি'),
        ],
        default='medium',
        verbose_name=_('তীব্রতা'),  # Severity
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('রোগ')
        verbose_name_plural = _('রোগসমূহ')
        ordering = ['name_bn']
        indexes = [
            models.Index(fields=['name_en'], name='idx_disease_name_en'),
            models.Index(fields=['crop_type'], name='idx_disease_crop'),
        ]

    def __str__(self):
        return f"{self.name_bn} ({self.name_en})"


class Recommendation(models.Model):
    """
    Treatment recommendations linked to diseases.
    Includes treatment, pesticide info, and prevention tips.
    """
    disease = models.ForeignKey(
        Disease,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('রোগ'),
    )
    treatment_bn = models.TextField(
        verbose_name=_('চিকিৎসা (বাংলা)'),  # Treatment (Bangla)
    )
    pesticide_bn = models.TextField(
        verbose_name=_('কীটনাশক (বাংলা)'),  # Pesticide (Bangla)
        blank=True,
    )
    pesticide_cost_bn = models.CharField(
        max_length=100,
        verbose_name=_('কীটনাশকের মূল্য (বাংলা)'),  # Pesticide Cost (Bangla)
        blank=True,
    )
    prevention_bn = models.TextField(
        verbose_name=_('প্রতিরোধ (বাংলা)'),  # Prevention (Bangla)
        blank=True,
    )
    dosage = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('মাত্রা'),  # Dosage
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('পরামর্শ')
        verbose_name_plural = _('পরামর্শসমূহ')

    def __str__(self):
        return f"পরামর্শ: {self.disease.name_bn}"


class DiseaseImage(models.Model):
    """
    Reference images for each disease.
    Used for training data reference and visual comparison.
    """
    disease = models.ForeignKey(
        Disease,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('রোগ'),
    )
    image = models.ImageField(
        upload_to='disease_references/',
        verbose_name=_('ছবি'),  # Image
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('ক্যাপশন'),
    )
    is_gallery = models.BooleanField(
        default=False,
        verbose_name=_('গ্যালারি ছবি'),  # Gallery Image
        help_text=_('Is this a morphologically similar disease image for the gallery?'),
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('রোগের ছবি')
        verbose_name_plural = _('রোগের ছবিসমূহ')

    def __str__(self):
        return f"{self.disease.name_bn} - ছবি"


class Detection(models.Model):
    """
    Stores each detection request and its results.
    Links user → uploaded image → predicted disease → recommendations.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('অপেক্ষমান')     # Pending
        COMPLETED = 'completed', _('সম্পন্ন')    # Completed
        FAILED = 'failed', _('ব্যর্থ')           # Failed

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='detections',
        verbose_name=_('ব্যবহারকারী'),
    )
    image = models.ImageField(
        upload_to='detections/%Y/%m/%d/',
        verbose_name=_('আপলোড করা ছবি'),  # Uploaded Image
    )
    disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detections',
        verbose_name=_('শনাক্তকৃত রোগ'),  # Detected Disease
    )
    confidence = models.FloatField(
        default=0.0,
        verbose_name=_('আত্মবিশ্বাস স্কোর'),  # Confidence Score
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('অবস্থা'),  # Status
        db_index=True,
    )
    result_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('ফলাফল ডেটা'),  # Result Data
    )
    is_bookmarked = models.BooleanField(
        default=False,
        verbose_name=_('বুকমার্ক'),  # Bookmarked
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('নোট'),  # Notes
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('শনাক্তকরণ')
        verbose_name_plural = _('শনাক্তকরণসমূহ')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_detection_user_date'),
            models.Index(fields=['status'], name='idx_detection_status'),
            models.Index(fields=['is_bookmarked'], name='idx_detection_bookmark'),
        ]

    def __str__(self):
        disease_name = self.disease.name_bn if self.disease else 'অজানা'
        return f"{self.user.username} — {disease_name} ({self.confidence:.0%})"

    @property
    def confidence_percent(self):
        """Return confidence as percentage string."""
        return f"{self.confidence * 100:.1f}%"


class InfoRequest(models.Model):
    """
    Tracks farmer requests for more information about an unverified disease.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='info_requests',
        verbose_name=_('ব্যবহারকারী'),
    )
    disease = models.ForeignKey(
        Disease,
        on_delete=models.CASCADE,
        related_name='info_requests',
        verbose_name=_('রোগ'),
    )
    message = models.TextField(
        blank=True,
        verbose_name=_('বার্তা'),
    )
    is_responded = models.BooleanField(
        default=False,
        verbose_name=_('উত্তর দেওয়া হয়েছে'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('তথ্যের অনুরোধ')
        verbose_name_plural = _('তথ্যের অনুরোধসমূহ')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.disease.name_en}"
