"""
Messaging Views — Chat interface and message handling.
"""

import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages as django_messages
from django.db.models import Q
from django.http import JsonResponse
from .models import ChatMessage, VoiceMessage
from accounts.models import User
from detection.models import InfoRequest

# Regex to find detection links in messages
DETECTION_LINK_RE = re.compile(r'/detection/(\d+)/')


class ChatListView(LoginRequiredMixin, View):
    """List all conversation partners for the current user."""

    template_name = 'messaging/chat_list.html'

    def get(self, request):
        user = request.user

        # Get unique conversation partners
        sent_to = ChatMessage.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
        received_from = ChatMessage.objects.filter(receiver=user).values_list('sender', flat=True).distinct()
        partner_ids = set(list(sent_to) + list(received_from))

        partners = User.objects.filter(id__in=partner_ids)

        # If farmer, also show available officers
        if user.is_farmer:
            officers = User.objects.filter(role=User.Role.OFFICER)
            available_officers = officers.exclude(id__in=partner_ids)
        else:
            available_officers = []

        # Count unread messages
        unread_count = ChatMessage.objects.filter(receiver=user, is_read=False).count()

        context = {
            'partners': partners,
            'available_officers': available_officers,
            'unread_count': unread_count,
        }
        return render(request, self.template_name, context)


class ChatDetailView(LoginRequiredMixin, View):
    """View conversation with a specific user and send messages."""

    template_name = 'messaging/chat_detail.html'

    def get(self, request, user_id):
        partner = get_object_or_404(User, id=user_id)

        # Get all messages between the two users
        chat_messages = list(ChatMessage.objects.filter(
            (Q(sender=request.user, receiver=partner) |
             Q(sender=partner, receiver=request.user))
        ))
        
        voice_messages = list(VoiceMessage.objects.filter(
            (Q(sender=request.user, receiver=partner) |
             Q(sender=partner, receiver=request.user))
        ))

        # Combine and sort by created_at
        all_messages = sorted(chat_messages + voice_messages, key=lambda x: x.created_at)

        # Mark received messages as read
        ChatMessage.objects.filter(
            sender=partner, receiver=request.user, is_read=False
        ).update(is_read=True)
        
        VoiceMessage.objects.filter(
            sender=partner, receiver=request.user, is_read=False
        ).update(is_read=True)

        # Extract detection IDs from all chat messages to show rich preview cards
        from detection.models import Detection
        detection_ids = set()
        for msg in chat_messages:
            if msg.message:
                matches = DETECTION_LINK_RE.findall(msg.message)
                for mid in matches:
                    detection_ids.add(int(mid))

        detections_map = {}
        if detection_ids:
            dets = Detection.objects.filter(id__in=detection_ids).select_related('disease')
            for det in dets:
                detections_map[det.id] = det

        # Attach detection objects directly to messages for easy template access
        for msg in chat_messages:
            msg.linked_detection = None
            if msg.message:
                match = DETECTION_LINK_RE.search(msg.message)
                if match:
                    det_id = int(match.group(1))
                    msg.linked_detection = detections_map.get(det_id)

        prefill_message = ""
        detection_id = request.GET.get('detection_id')
        if detection_id:
            detection = Detection.objects.filter(id=detection_id).select_related('disease').first()
            if detection and detection.disease:
                url = request.build_absolute_uri(f"/detection/{detection.id}/")
                prefill_message = f"আসসালামু আলাইকুম, আমি আমার ফসলে একটি রোগ শনাক্ত করেছি: {detection.disease.name_bn}। বিস্তারিত দেখতে এই লিংকে যান: {url} \nদয়া করে আমাকে পরামর্শ দিন।"

        context = {
            'partner': partner,
            'all_messages': all_messages,
            'prefill_message': prefill_message,
        }
        return render(request, self.template_name, context)

    def post(self, request, user_id):
        partner = get_object_or_404(User, id=user_id)
        message_text = request.POST.get('message', '').strip()

        if message_text:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=partner,
                message=message_text,
            )
            django_messages.success(request, 'বার্তা পাঠানো হয়েছে!')  # Message sent

        return redirect('messaging:chat_detail', user_id=user_id)


class VoiceMessageView(LoginRequiredMixin, View):
    """Handle voice message upload (mock implementation)."""

    def post(self, request, user_id):
        partner = get_object_or_404(User, id=user_id)
        audio_file = request.FILES.get('audio_file')

        if audio_file:
            VoiceMessage.objects.create(
                sender=request.user,
                receiver=partner,
                audio_file=audio_file,
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'ভয়েস বার্তা পাঠানো হয়েছে!'})
            django_messages.success(request, 'ভয়েস বার্তা পাঠানো হয়েছে!')  # Voice message sent
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'অডিও ফাইল পাওয়া যায়নি।'}, status=400)
            django_messages.error(request, 'অডিও ফাইল পাওয়া যায়নি।')  # Audio file not found

        return redirect('messaging:chat_detail', user_id=user_id)


class UnreadNotificationsView(LoginRequiredMixin, View):
    """AJAX endpoint to fetch unread notifications for the bell icon and toasts."""

    def get(self, request):
        user = request.user
        notifications = []

        # 1. Check Unread Chat Messages
        from django.urls import reverse
        unread_chats = ChatMessage.objects.filter(receiver=user, is_read=False).select_related('sender').order_by('-created_at')[:5]
        for msg in unread_chats:
            notifications.append({
                'id': f"chat_{msg.id}",
                'type': 'chat',
                'title': f"{msg.sender.username} থেকে নতুন বার্তা",
                'message': msg.message[:50] + '...' if len(msg.message) > 50 else msg.message,
                'url': reverse('messaging:chat_detail', kwargs={'user_id': msg.sender.id})
            })

        # 2. For Officers: Check Unread/Unresponded InfoRequests
        if user.is_officer or user.is_superuser or user.is_admin_user:
            from django.urls import reverse
            recent_requests = InfoRequest.objects.filter(is_responded=False).select_related('user', 'disease').order_by('-created_at')[:5]
            for req in recent_requests:
                disease_name = req.disease.name_en if req.disease.name_bn == req.disease.name_en else f"{req.disease.name_en} ({req.disease.name_bn})"
                base_url = reverse('adminpanel:add_disease')
                notifications.append({
                    'id': f"req_{req.id}",
                    'type': 'inforequest',
                    'title': "নতুন রোগের তথ্য অনুরোধ",
                    'message': f"{req.user.username} {disease_name} সম্পর্কে জানতে চেয়েছেন।",
                    'url': f"{base_url}?edit={req.disease.id}&req_id={req.id}"
                })

        return JsonResponse({
            'count': len(notifications),
            'notifications': notifications
        })
