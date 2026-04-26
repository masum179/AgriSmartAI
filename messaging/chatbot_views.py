"""
Chatbot Views — AI-powered agricultural assistant using Google Gemini (google-genai SDK).
Available to Farmers and Agricultural Officers.
"""

import json
import logging
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)

# System prompt for the agricultural AI assistant
SYSTEM_PROMPT = """তুমি AgriSmart AI-র কৃষি সহকারী। তুমি বাংলাদেশী কৃষকদের এবং কৃষি কর্মকর্তাদের সাহায্য করো।

তোমার কাজ:
- ফসলের রোগ সম্পর্কে তথ্য দেওয়া (ধান, গম, পাট, শাকসবজি, ফল ইত্যাদি)
- কীটনাশক ও সার ব্যবহারের পরামর্শ দেওয়া
- আবহাওয়া ও মৌসুম অনুযায়ী চাষাবাদের পরামর্শ দেওয়া
- রোগ প্রতিরোধ ও চিকিৎসার পদ্ধতি ব্যাখ্যা করা
- কৃষিজ সমস্যার সহজ ও ব্যবহারিক সমাধান দেওয়া

নিয়মাবলী:
- সহজ ও সংক্ষিপ্ত ভাষায় উত্তর দাও (সর্বোচ্চ ৩-৪ বাক্য)
- ব্যবহারকারী ইংরেজিতে প্রশ্ন করলে ইংরেজিতে উত্তর দাও
- ব্যবহারকারী বাংলায় প্রশ্ন করলে বাংলায় উত্তর দাও
- কৃষি বিষয়ের বাইরের প্রশ্নে বিনয়ের সাথে বলো যে তুমি শুধু কৃষি বিষয়ে সাহায্য করতে পারো
- সবসময় বন্ধুত্বপূর্ণ ও সহায়ক থাকো"""

# ─── Gemini Setup (new google-genai SDK) ─────────────────────────────────────
GEMINI_AVAILABLE = False
_genai_client = None

try:
    from google import genai
    from google.genai import types as genai_types
    _genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Gemini initialization failed: {e}")

# In-memory chat history per user (session-scoped, no DB needed)
_CHAT_HISTORIES = {}


class ChatbotPageView(LoginRequiredMixin, View):
    """Render the chatbot UI page."""

    template_name = 'messaging/chatbot.html'

    def get(self, request):
        # Retrieve existing history if any
        uid = request.user.id
        history = _CHAT_HISTORIES.get(uid, [])
        
        # history is a list of strings: [user_msg1, bot_msg1, user_msg2, bot_msg2, ...]
        # We need to pair them up for the template
        chat_pairs = []
        for i in range(0, len(history) - 1, 2):
            chat_pairs.append({
                'user': history[i],
                'bot': history[i+1]
            })

        return render(request, self.template_name, {
            'gemini_available': GEMINI_AVAILABLE and settings.GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE',
            'chat_history': chat_pairs,
        })


class ChatbotAPIView(LoginRequiredMixin, View):
    """AJAX endpoint: receives user message → Gemini API → JSON reply."""

    def post(self, request):
        # Parse request body
        try:
            body = json.loads(request.body)
            user_message = body.get('message', '').strip()
        except (json.JSONDecodeError, AttributeError):
            user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'বার্তা ফাঁকা।'}, status=400)

        api_ready = GEMINI_AVAILABLE and settings.GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE'

        if not api_ready:
            uid = request.user.id
            if uid not in _CHAT_HISTORIES:
                _CHAT_HISTORIES[uid] = []
            reply = self._mock_reply(user_message)
            _CHAT_HISTORIES[uid].append(user_message)
            _CHAT_HISTORIES[uid].append(reply)
            return JsonResponse({'reply': reply, 'mock': True})

        try:
            uid = request.user.id

            # Build conversation history
            if uid not in _CHAT_HISTORIES:
                _CHAT_HISTORIES[uid] = []

            history = _CHAT_HISTORIES[uid]

            # Build contents list for the API call
            from google.genai import types as genai_types

            contents = [genai_types.Content(
                role='user' if i % 2 == 0 else 'model',
                parts=[genai_types.Part(text=msg)]
            ) for i, msg in enumerate(history)]

            # Add current user message
            contents.append(genai_types.Content(
                role='user',
                parts=[genai_types.Part(text=user_message)]
            ))

            response = _genai_client.models.generate_content(
                model='gemini-2.0-flash',
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=400,
                ),
                contents=contents,
            )

            reply = response.text.strip()

            # Maintain rolling history (last 10 exchanges = 20 items)
            history.append(user_message)
            history.append(reply)
            if len(history) > 20:
                _CHAT_HISTORIES[uid] = history[-20:]

            return JsonResponse({'reply': reply, 'mock': False})

        except Exception as e:
            logger.error(f"Gemini API error for user {request.user.id}: {e}")
            return JsonResponse({
                'reply': 'দুঃখিত, AI সহকারী এই মুহূর্তে উপলব্ধ নেই। পরে চেষ্টা করুন।',
                'mock': True,
            })

    def _mock_reply(self, message: str) -> str:
        """Smart fallback when Gemini API key is not configured."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['blast', 'ব্লাস্ট', 'বাদামি', 'brown spot']):
            return 'ধানের ব্লাস্ট রোগে ট্রাইসাইক্লাজোল ৭৫ WP ছত্রাকনাশক ব্যবহার করুন। প্রতি লিটার পানিতে ০.৬ গ্রাম মিশিয়ে স্প্রে করুন। আক্রান্ত এলাকায় পানি নিষ্কাশন নিশ্চিত করুন।'
        elif any(w in msg_lower for w in ['সার', 'fertilizer', 'urea', 'ইউরিয়া']):
            return 'ধানে প্রতি বিঘায় ৩০-৩৫ কেজি ইউরিয়া সার প্রয়োজন। তিন ভাগে দিন: রোপণের সময়, ২৫ দিন ও ৫০ দিন পর। TSP ও MoP সার বেসাল ডোজে দিন।'
        elif any(w in msg_lower for w in ['পোকা', 'insect', 'pest', 'কীটপতঙ্গ']):
            return 'পোকামাকড় দমনে ইমিডাক্লোপ্রিড বা ক্লোরপাইরিফস ব্যবহার করুন। সন্ধ্যায় স্প্রে করুন। জৈব পদ্ধতিতে নিম তেল ও সাবান পানি কার্যকর।'
        elif any(w in msg_lower for w in ['হলুদ', 'yellow', 'পাতা হলুদ']):
            return 'পাতা হলুদ হওয়া সাধারণত নাইট্রোজেন ঘাটতির লক্ষণ। ইউরিয়া সার প্রয়োগ করুন। এছাড়া আয়রন ঘাটতিতে ফেরাস সালফেট স্প্রে করুন।'
        elif any(w in msg_lower for w in ['weather', 'বৃষ্টি', 'আবহাওয়া', 'বন্যা']):
            return 'বর্ষা মৌসুমে ছত্রাকজনিত রোগের প্রকোপ বেশি হয়। ফসলে নিয়মিত নজর রাখুন। জমিতে পানি জমলে দ্রুত নিষ্কাশনের ব্যবস্থা করুন।'
        elif any(w in msg_lower for w in ['hello', 'hi', 'হ্যালো', 'নমস্কার', 'সালাম', 'আসসালামু']):
            return 'আস্সালামু আলাইকুম! আমি AgriSmart AI-র কৃষি সহকারী। ফসলের রোগ, সার, কীটনাশক বা চাষাবাদ সম্পর্কে যেকোনো প্রশ্ন করুন।'
        else:
            return (
                'আপনার প্রশ্নের জন্য ধন্যবাদ। AI চ্যাটবট সক্রিয় করতে '
                'settings.py-তে আপনার Gemini API Key যোগ করুন '
                '(https://aistudio.google.com/app/apikey থেকে বিনামূল্যে পাওয়া যায়)।'
            )
