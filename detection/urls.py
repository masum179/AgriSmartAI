"""
Detection URL Configuration
"""

from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('upload/', views.UploadView.as_view(), name='upload'),
    path('result/<int:pk>/', views.ResultView.as_view(), name='result'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('bookmark/<int:pk>/', views.ToggleBookmarkView.as_view(), name='toggle_bookmark'),
    path('request-info/<int:disease_id>/', views.RequestInfoView.as_view(), name='request_info'),
    path('delete/<int:pk>/', views.DeleteDetectionView.as_view(), name='delete_detection'),
    path('diseases/', views.DiseaseListView.as_view(), name='disease_list'),
    path('diseases/add/', views.OfficerAddDiseaseView.as_view(), name='officer_add_disease'),
]
