import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

ICON_PATH = "assets/YanTimur.png"
ICON_PATH_RIGHT = "assets/kullanilmayan/Alper.png"
ICON_ICO = "assets/Timur.ico"

WINDOW_WIDTH = 200
WINDOW_HEIGHT = 200
LOADING_DURATION_MS = 3000  # 3 saniyede dolacak

# Chat window ayarları
CHAT_WINDOW_WIDTH = 500
CHAT_WINDOW_HEIGHT = 600

# ============================================
# GEMINI API CONFIGURATIONS
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Ortam değişkeninden yükle
GEMINI_MODEL = "gemini-2.5-flash-lite" # Gemini model seçimi

# ============================================
# EMBEDDING MODEL (Duygu Analizi)
# ============================================
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# ============================================
# DUYGU ETİKETLERİ (8 Emotion Tags)
# ============================================
EMOTION_TAGS = [
    "panik",       # Panic/Fear
    "öfke",        # Anger
    "üzüntü",      # Sadness
    "endişe",      # Anxiety
    "sevinç",      # Joy
    "merak",       # Curiosity
    "şaşkınlık",   # Surprise
    "kayıtsızlık"  # Neutral/Indifference
]

# Duygu etiketi reference embeddings (embedding model ile ön-hesaplanacak)
EMOTION_REFERENCE_EMBEDDINGS = {}