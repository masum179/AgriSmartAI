"""
Messaging Models — Chat messages and voice messages.
Supports farmer-officer communication.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ChatMessage(models.Model):
    """
    Text chat messages between farmers and officers.
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('প্রেরক'),  # Sender
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('প্রাপক'),  # Receiver
    )
    message = models.TextField(
        verbose_name=_('বার্তা'),  # Message
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('পঠিত'),  # Read
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('চ্যাট বার্তা')
        verbose_name_plural = _('চ্যাট বার্তাসমূহ')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'receiver'], name='idx_chat_sender_receiver'),
            models.Index(fields=['is_read'], name='idx_chat_is_read'),
            models.Index(fields=['-created_at'], name='idx_chat_created'),
        ]

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.message[:50]}"


class VoiceMessage(models.Model):
    """
    Voice messages between farmers and officers.
    Stores audio file references.
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_voice_messages',
        verbose_name=_('প্রেরক'),
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_voice_messages',
        verbose_name=_('প্রাপক'),
    )
    audio_file = models.FileField(
        upload_to='voice_messages/%Y/%m/%d/',
        verbose_name=_('অডিও ফাইল'),  # Audio File
    )
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name=_('সময়কাল (সেকেন্ড)'),  # Duration (seconds)
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('শোনা হয়েছে'),  # Listened
    )
    is_reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('উত্তরে'),  # In reply to
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('ভয়েস বার্তা')
        verbose_name_plural = _('ভয়েস বার্তাসমূহ')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'receiver'], name='idx_voice_sender_receiver'),
        ]

    def __str__(self):
        return f"ভয়েস: {self.sender.username} → {self.receiver.username}"
