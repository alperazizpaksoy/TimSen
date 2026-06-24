"""
TimSen Emotion Analyzer
Kullanıcı mesajından duygu etiketini çıkarır.
Embedding modeli ile duygu analizi yapır ve en yakın etiketi döner.
"""

from sentence_transformers import SentenceTransformer, util
from config import EMBEDDING_MODEL, EMOTION_TAGS, EMOTION_REFERENCE_EMBEDDINGS
import torch


class EmotionAnalyzer:
    """Embedding modeli ile duygu analizi yapan sınıf"""
    
    def __init__(self):
        print("EmotionAnalyzer: Multilingual embedding modeli yükleniyor...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Duygu etiketi embeddings'lerini ön-hesapla
        self._initialize_emotion_embeddings()
    
    def _initialize_emotion_embeddings(self):
        """Duygu etiketlerinin embeddings'lerini hesapla ve cache'le"""
        global EMOTION_REFERENCE_EMBEDDINGS
        
        if not EMOTION_REFERENCE_EMBEDDINGS:
            print("EmotionAnalyzer: Duygu etiketi embeddings'leri hesaplanıyor...")
            
            # Her duygu etiketi için örnek cümleler (çokdillilik için)
            emotion_examples = {
                "panik": [
                    "panik halindeyim",
                    "çok korkuyorum",
                    "dehşet içindeyim",
                    "I'm panicking",
                    "terrified"
                ],
                "öfke": [
                    "çok öfkeliyim",
                    "çok kızgınım",
                    "hiddetim bozuldu",
                    "I'm angry",
                    "furious"
                ],
                "üzüntü": [
                    "çok üzgünüm",
                    "depresyfim",
                    "mutsuz hissediyorum",
                    "I'm sad",
                    "devastated"
                ],
                "endişe": [
                    "endişeliyim",
                    "kaygılıyım",
                    "tedirgin",
                    "I'm anxious",
                    "worried"
                ],
                "sevinç": [
                    "çok mutluyum",
                    "harika hissediyorum",
                    "sevinçliyim",
                    "I'm happy",
                    "delighted"
                ],
                "merak": [
                    "merak ediyorum",
                    "bilmek istiyorum",
                    "nasıl oluyor",
                    "I'm curious",
                    "interesting"
                ],
                "şaşkınlık": [
                    "şaşkınım",
                    "İnanamıyorum",
                    "beklemiyordum",
                    "I'm surprised",
                    "shocking"
                ],
                "kayıtsızlık": [
                    "umurumda değil",
                    "ne de olsa",
                    "fark etmez",
                    "I don't care",
                    "neutral"
                ]
            }
            
            # Her duygu için embeddings hesapla ve ortalamasını al
            for emotion, examples in emotion_examples.items():
                embeddings = self.model.encode(examples, convert_to_tensor=True)
                # Tüm örnek embeddings'lerin ortalaması
                avg_embedding = torch.mean(embeddings, dim=0)
                EMOTION_REFERENCE_EMBEDDINGS[emotion] = avg_embedding
            
            print(f"✓ {len(EMOTION_REFERENCE_EMBEDDINGS)} duygu etiketi hazırlandı")
    
    def analyze(self, user_message: str) -> str:
        """
        Kullanıcı mesajının duygusunu analiz eder.
        
        Args:
            user_message: Kullanıcı mesajı
        
        Returns:
            En yakın duygu etiketi (str)
        """
        # Kullanıcı mesajının embedding'ini al
        user_embedding = self.model.encode(user_message, convert_to_tensor=True)
        
        # Her duygu etiketi ile kosinüs benzerliğini hesapla
        similarities = {}
        for emotion, emotion_embedding in EMOTION_REFERENCE_EMBEDDINGS.items():
            sim = util.pytorch_cos_sim(user_embedding, emotion_embedding)[0][0].item()
            similarities[emotion] = sim
        
        # En yüksek benzerliğe sahip duyguyu döner
        detected_emotion = max(similarities, key=similarities.get)
        return detected_emotion
    
    def analyze_with_score(self, user_message: str) -> tuple:
        """
        Kullanıcı mesajının duygusunu analiz eder (skor ile).
        
        Args:
            user_message: Kullanıcı mesajı
        
        Returns:
            (emotion_tag, confidence_score)
        """
        # Kullanıcı mesajının embedding'ini al
        user_embedding = self.model.encode(user_message, convert_to_tensor=True)
        
        # Her duygu etiketi ile kosinüs benzerliğini hesapla
        similarities = {}
        for emotion, emotion_embedding in EMOTION_REFERENCE_EMBEDDINGS.items():
            sim = util.pytorch_cos_sim(user_embedding, emotion_embedding)[0][0].item()
            similarities[emotion] = sim
        
        # En yüksek benzerliğe sahip duyguyu döner
        detected_emotion = max(similarities, key=similarities.get)
        confidence = similarities[detected_emotion]
        
        return detected_emotion, confidence
