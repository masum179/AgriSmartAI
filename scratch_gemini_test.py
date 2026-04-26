import os
import sys
import json
import base64

# Add project directory to Python path
sys.path.append('e:\\AgriSmartAI')

from django.conf import settings
from google import genai
from google.genai import types

# Configure a minimal settings block so we can read the API key
try:
    settings.configure(GEMINI_API_KEY=os.environ.get('GEMINI_API_KEY', 'AIzaSyAAkAWaXfTGCn2GpXEic7rsRopttwUVIvE'))
except Exception:
    pass

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# dummy image data for testing
dummy_img = b"GIF89a\x01\x00\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;"

prompt = """
Analyze this image of a crop plant and determine if there is a disease.
Return a JSON object with two fields:
- disease_name: The English name of the disease, e.g., "Rice Blast". Return "Unknown Disease" if you are not sure or if it's healthy, return "Healthy".
- confidence_score: A number between 0 and 100 representing your confidence.
"""

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_bytes(dummy_img, mime_type='image/gif'),
                    types.Part.from_text(text=prompt)
                ]
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
