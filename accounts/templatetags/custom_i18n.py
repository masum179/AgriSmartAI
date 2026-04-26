import json
import os
from django import template
from django.conf import settings

register = template.Library()

# Load translations once into memory
TRANSLATIONS = {}
trans_file = os.path.join(settings.BASE_DIR, 'translations.json')
if os.path.exists(trans_file):
    with open(trans_file, 'r', encoding='utf-8') as f:
        try:
            TRANSLATIONS = json.load(f)
        except json.JSONDecodeError:
            pass

@register.simple_tag(takes_context=True)
def t(context, text):
    """
    Translates 'text' to English if request.session['lang'] == 'en'.
    Otherwise returns 'text' (assumes text is Bangla).
    """
    request = context.get('request')
    if not request:
        return text
    
    lang = request.session.get('lang', 'bn')
    if lang == 'en':
        return TRANSLATIONS.get(text, text)
    return text
