# 🌿 AgriSmart AI

**AgriSmart AI** is an AI-powered crop disease detection and agricultural communication platform designed to empower farmers and agricultural officers. It uses advanced machine learning (HuggingFace + Gemini) to diagnose plant diseases from leaf images in seconds.

---

## 🚀 Key Features
- **AI Diagnostics**: Instant disease identification using advanced machine learning.
- **Multilingual Support**: Full support for **Bengali (বাংলা)** and English.
- **Notification System**: Real-time alerts for messages and new disease identification requests.
- **Officer Dashboard**: Tools for agricultural officers to verify AI results and provide expert advice.
- **Dual-AI Fallback**: Automatically switches to Gemini if HuggingFace is rate-limited or loading.
- **Farmer History**: Persistent history of all scans with bookmarks for important diseases.

---

## 🔐 Default Credentials (Test Accounts)

For testing purposes, you can use the following pre-seeded accounts:

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Officer** | `officer1` | `officer123` |
| **Farmer** | `farmer1` | `farmer123` |
| **Farmer** | `farmer2` | `farmer123` |

---

## 🛠️ Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/masum179/AgriSmartAI.git
   cd AgriSmartAI
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   HF_TOKEN=your_huggingface_tokens_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Initialize Database:**
   ```bash
   python manage.py migrate
   python manage.py seed_data
   python seed_plantvillage.py
   ```

6. **Run Server:**
   ```bash
   python manage.py runserver
   ```

---

## 🌍 Deployment on Render

This project is optimized for **Render**. It includes a `render.yaml` blueprint and a `build.sh` script for automatic deployment.

1. Connect your repo to Render.
2. Select **"Blueprint"** or create a **"Web Service"**.
3. Add your `HF_TOKEN` and `GEMINI_API_KEY` to the Environment settings.

---

Developed with ❤️ for the agricultural community.




## 🚀 Key Features
- **AI Diagnostics**: Instant disease identification using HuggingFace & Gemini.
- **🤖 AI Agri-Assistant**: Intelligent Gemini-powered chatbot for instant farming advice.
- **🎙️ Voice & Text Messaging**: Accessibility-focused communication between farmers and officers.
- **Multilingual Support**: Full support for **Bengali (বাংলা)** and English.
- **Officer Dashboard**: Tools for agricultural officers to verify AI results and provide expert advice.
- **Farmer History**: Persistent history of all scans with bookmarks for important diseases.

