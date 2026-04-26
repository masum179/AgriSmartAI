"""
Detection Admin — Disease, Recommendation, Detection admin config.
"""

from django.contrib import admin
from .models import Disease, Recommendation, DiseaseImage, Detection


class RecommendationInline(admin.TabularInline):
    model = Recommendation
    extra = 1


class DiseaseImageInline(admin.TabularInline):
    model = DiseaseImage
    extra = 1


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_bn', 'name_en', 'crop_type', 'severity', 'is_active')
    list_filter = ('severity', 'crop_type', 'is_active')
    search_fields = ('name_bn', 'name_en')
    inlines = [RecommendationInline, DiseaseImageInline]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('disease', 'treatment_bn', 'is_active')
    list_filter = ('is_active', 'disease')
    search_fields = ('treatment_bn', 'pesticide_bn')


@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'disease', 'confidence', 'status', 'is_bookmarked', 'created_at')
    list_filter = ('status', 'is_bookmarked', 'created_at')
    search_fields = ('user__username', 'disease__name_bn')
    readonly_fields = ('result_data', 'created_at', 'updated_at')
