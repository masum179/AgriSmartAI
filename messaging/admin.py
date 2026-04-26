"""
Messaging Admin Configuration
"""

from django.contrib import admin
from .models import ChatMessage, VoiceMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'message')


@admin.register(VoiceMessage)
class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'duration', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
