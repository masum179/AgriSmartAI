"""
Messaging URL Configuration
"""

from django.urls import path
from . import views
from .chatbot_views import ChatbotPageView, ChatbotAPIView

app_name = 'messaging'

urlpatterns = [
    path('', views.ChatListView.as_view(), name='chat_list'),
    path('chat/<int:user_id>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('voice/<int:user_id>/', views.VoiceMessageView.as_view(), name='voice_message'),
    path('api/notifications/unread/', views.UnreadNotificationsView.as_view(), name='unread_notifications'),
    path('chatbot/', ChatbotPageView.as_view(), name='chatbot'),
    path('api/chatbot/', ChatbotAPIView.as_view(), name='chatbot_api'),
]
