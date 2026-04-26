"""
Admin Panel URL Configuration
"""

from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('users/', views.ManageUsersView.as_view(), name='manage_users'),
    path('users/add/', views.AddUserView.as_view(), name='add_user'),
    path('users/<int:pk>/toggle/', views.ToggleUserStatusView.as_view(), name='toggle_user'),
    path('users/<int:pk>/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    path('diseases/', views.ManageDiseasesView.as_view(), name='manage_diseases'),
    path('diseases/add/', views.AddDiseaseView.as_view(), name='add_disease'),
    path('diseases/<int:pk>/delete/', views.DeleteDiseaseView.as_view(), name='delete_disease'),
    path('recommendations/', views.ManageRecommendationsView.as_view(), name='manage_recommendations'),
    path('logs/', views.DetectionLogsView.as_view(), name='detection_logs'),
    path('logs/<int:pk>/delete/', views.DeleteDetectionLogView.as_view(), name='delete_detection_log'),
]
