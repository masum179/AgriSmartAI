"""
AI Service — Crop disease prediction using HuggingFace Inference API.
Uses the linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification model
trained on the PlantVillage dataset.
Falls back to mock prediction if the API is unavailable.
"""

import random
import logging
import os
import mimetypes
import requests
from django.conf import settings
from detection.models import Disease

logger = logging.getLogger(__name__)

# HuggingFace Inference API
HF_API_URL = "https://router.huggingface.co/hf-inference/models/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"


def mock_predict_disease(image_path):
    """
    AI prediction using HuggingFace plant disease classification model.
    Falls back to mock if the API is unavailable or HF_TOKEN is not set.
    """
    diseases = Disease.objects.filter(is_active=True)
    predicted_disease_name = None
    confidence = 0.0

    # Try HuggingFace Inference API (Supports multiple tokens separated by comma)
    hf_tokens_raw = getattr(settings, 'HF_TOKEN', '')
    hf_tokens = [t.strip() for t in hf_tokens_raw.split(',') if t.strip()]
    
    if hf_tokens:
        for hf_token in hf_tokens:
            if predicted_disease_name:
                break  # Already found a match with a previous token
                
            try:
                mime_type, _ = mimetypes.guess_type(image_path)
                if not mime_type:
                    mime_type = 'image/jpeg'

                with open(image_path, "rb") as f:
                    image_data = f.read()

                headers = {
                    "Authorization": f"Bearer {hf_token}",
                    "Content-Type": mime_type,
                }
                
                # Retry loop for HuggingFace "Model Loading" (503) error
                import time
                max_retries = 3
                results = None
                for attempt in range(max_retries):
                    response = requests.post(HF_API_URL, headers=headers, data=image_data, timeout=30)
                    
                    if response.status_code == 200:
                        results = response.json()
                        break
                    elif response.status_code == 503 and attempt < max_retries - 1:
                        logger.info(f"HF Model loading (503). Retrying in 5s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(5)
                    elif response.status_code == 429: # Rate limit
                        logger.warning(f"HF Token Rate Limited (429). Switching to next token...")
                        break
                    else:
                        logger.warning(f"HF API error {response.status_code} with current token.")
                        break

                if results and isinstance(results, list) and len(results) > 0:
                    top_result = results[0]
                    raw_label = top_result.get("label", "")
                    api_confidence = float(top_result.get("score", 0.0))
                    
                    # Convert HF label format "Tomato___Early_blight" → "Tomato Early Blight"
                    clean_name = raw_label.replace("___", " ").replace("_", " ").strip()
                    is_healthy = "healthy" in clean_name.lower()

                    # Find the matching disease from the database
                    for d in diseases:
                        if d.name_en.lower() == clean_name.lower():
                            predicted_disease_name = d.name_bn
                            confidence = api_confidence
                            break

                    # Try smart partial matching if exact match fails
                    if not predicted_disease_name:
                        clean_words = set(w for w in clean_name.lower().replace('(', '').replace(')', '').split() if w not in ['with', 'and', 'the', 'of', 'in', 'disease'])
                        
                        best_match = None
                        best_score = 0
                        
                        for d in diseases:
                            d_words = set(w for w in d.name_en.lower().replace('(', '').replace(')', '').split() if w not in ['with', 'and', 'the', 'of', 'in', 'disease'])
                            
                            if clean_words and d_words:
                                # Calculate Jaccard-like similarity based on intersection
                                intersection = len(clean_words.intersection(d_words))
                                score = intersection / max(len(clean_words), len(d_words))
                                
                                # Substring match as backup
                                if clean_name.lower() in d.name_en.lower() or d.name_en.lower() in clean_name.lower():
                                    score = max(score, 0.8)

                                if score > 0.55 and score > best_score:
                                    best_match = d
                                    best_score = score
                                    
                        if best_match:
                            predicted_disease_name = best_match.name_bn
                            confidence = api_confidence

                    # If still no match, create a pending disease record
                    if not predicted_disease_name and clean_name and not is_healthy:
                        new_disease, created = Disease.objects.get_or_create(
                            name_en__iexact=clean_name,
                            defaults={
                                'name_en': clean_name,
                                'name_bn': clean_name,  # Temporary — officer will translate
                                'crop_type': clean_name.split()[0] if clean_name else 'Unknown',
                                'is_active': False,
                            }
                        )
                        predicted_disease_name = new_disease.name_bn
                        confidence = api_confidence

                    logger.info(f"HF API prediction: {clean_name} (confidence: {api_confidence:.2f})")
            except Exception as e:
                logger.error(f"HuggingFace API error with token: {e}")
    else:
        logger.warning("HF_TOKEN is not set. Skipping HuggingFace API.")

    # FALLBACK: Use Gemini API if HuggingFace failed or is not available
    if not predicted_disease_name:
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
        if gemini_key:
            try:
                import google.generativeai as genai
                from PIL import Image

                logger.info("Trying Gemini Vision API as fallback...")
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                img = Image.open(image_path)
                prompt = (
                    "Identify the crop disease in this image. "
                    "Respond ONLY with the English name of the crop and the disease name, "
                    "for example 'Tomato Early Blight' or 'Corn Gray Leaf Spot'. "
                    "If the plant is healthy, respond with '[Crop Name] Healthy'."
                )
                
                response = model.generate_content([prompt, img])
                try:
                    clean_name = response.text.strip().replace('\n', '').replace('*', '')
                except (AttributeError, ValueError):
                    # Handle safety block or empty response
                    logger.warning("Gemini API blocked the response or returned no text.")
                    clean_name = ""

                logger.info(f"Gemini API returned: {clean_name}")
                
                if clean_name:
                    api_confidence = 0.95  # Gemini doesn't return raw confidences like this
                    is_healthy = "healthy" in clean_name.lower()
                    
                    # 1. Exact Match (Clean punctuation from both sides)
                    import string
                    target_name = clean_name.translate(str.maketrans('', '', string.punctuation)).lower().strip()

                    for d in diseases:
                        db_name_en = d.name_en.translate(str.maketrans('', '', string.punctuation)).lower().strip()
                        if db_name_en == target_name:
                            predicted_disease_name = d.name_bn
                            confidence = api_confidence
                            break
                            
                    # 2. Smart Fuzzy Match
                    if not predicted_disease_name:
                        # Strip punctuation before splitting into words
                        clean_stripped = clean_name.translate(str.maketrans('', '', string.punctuation)).lower()
                        clean_words = set(w for w in clean_stripped.split() if w not in ['with', 'and', 'the', 'of', 'in', 'disease', 'crop', 'plant'])
                        
                        best_match = None
                        best_score = 0
                        for d in diseases:
                            d_stripped = d.name_en.translate(str.maketrans('', '', string.punctuation)).lower()
                            d_words = set(w for w in d_stripped.split() if w not in ['with', 'and', 'the', 'of', 'in', 'disease', 'crop', 'plant'])
                            
                            if clean_words and d_words:
                                intersection = len(clean_words.intersection(d_words))
                                score = intersection / max(len(clean_words), len(d_words))
                                if clean_stripped in d_stripped or d_stripped in clean_stripped:
                                    score = max(score, 0.8)
                                if score > 0.55 and score > best_score:
                                    best_match = d
                                    best_score = score
                        if best_match:
                            predicted_disease_name = best_match.name_bn
                            confidence = api_confidence
                            
                    # 3. Create Pending Disease
                    if not predicted_disease_name and not is_healthy:
                        new_disease, created = Disease.objects.get_or_create(
                            name_en__iexact=clean_name,
                            defaults={
                                'name_en': clean_name,
                                'name_bn': clean_name,
                                'crop_type': clean_name.split()[0] if clean_name else 'Unknown',
                                'is_active': False,
                            }
                        )
                        predicted_disease_name = new_disease.name_bn
                        confidence = api_confidence
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
        else:
            logger.warning("GEMINI_API_KEY is not set. Skipping Gemini fallback.")

    # Return error if API fails
    if not predicted_disease_name:
        return {'success': False, 'error': 'রোগ শনাক্ত করা সম্ভব হয়নি। দয়া করে পরিষ্কার ছবি দিয়ে আবার চেষ্টা করুন অথবা সার্ভার ঠিক আছে কিনা নিশ্চিত করুন।'}
    else:
        predicted_disease = Disease.objects.filter(name_bn=predicted_disease_name).first()

    confidence = round(confidence, 4)

    # Fetch recommendations for the predicted disease
    recommendations = predicted_disease.recommendations.filter(is_active=True)
    rec_list = []
    for rec in recommendations:
        rec_list.append({
            'treatment': rec.treatment_bn,
            'pesticide': rec.pesticide_bn,
            'prevention': rec.prevention_bn,
            'dosage': rec.dosage,
        })

    return {
        'success': True,
        'disease_id': predicted_disease.id,
        'disease_name_bn': predicted_disease.name_bn,
        'disease_name_en': predicted_disease.name_en,
        'crop_type': predicted_disease.crop_type,
        'severity': predicted_disease.severity,
        'confidence': confidence,
        'recommendations': rec_list,
    }
