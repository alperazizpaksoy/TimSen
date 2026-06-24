"""
TimSen Gemini Client
Google Gemini API ile sohbet yönetimi.
Senaryo bazlı, context'e duyarlı yanıtlar üretir.
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from typing import List, Dict, Optional

class GeminiClient:
    """Google Gemini API ile iletişim kuran sınıf"""
    
    def __init__(self):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "gizli_key":
            raise ValueError(
                "❌ GEMINI_API_KEY bulunamadı veya değiştirilmemiş!\n"
                "Lütfen config.py dosyasındaki key'i güncelleyin."
            )
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = None
        self.chat_history = []
        self.scenario_context = None
        self.user_role = None
        self.ai_role = None
        self.conversation_log = []
        
        print(f"✓ Gemini Client API anahtarı onaylandı (Model: {GEMINI_MODEL})")
    
    def set_scenario(self, scenario_description: str):
        """Senaryo bağlamını ayarla (uyumluluk için)"""
        self.scenario_context = scenario_description
        self.chat_history = []
        self.conversation_log = []
        
        system_prompt = f"Senin senaryon: {scenario_description}\n\nBu senaryoya uygun olarak, rolden hiç çıkmadan iletişim kur."
        
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_prompt
        )
        
        print(f"📋 Senaryo modele entegre edildi: {scenario_description[:50]}...")
    
    def init_roleplay(self, user_role: str, ai_role: str, scenario: str):
        """Role-play konuşması başlat"""
        self.user_role = user_role
        self.ai_role = ai_role
        self.scenario_context = scenario
        self.chat_history = []
        self.conversation_log = []
        
        system_prompt = f"""Sen rol oynama asistanısın.
Kurallar:
- Senin rolün: {ai_role}
- Kullanıcının rolü: {user_role}
- Senaryo: {scenario}

ÖNEMLI:
1. Her zaman rolde kal, asistan olduğunu söyleme
2. Doğal, gerçekçi ve canlı cevaplar ver
3. Senaryoya uygun davran
4. Kısa ve akıcı konuş"""
        
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_prompt
        )
        
        print(f"✓ Role-play başlatıldı:")
        print(f"  • AI Rolü: {ai_role}")
        print(f"  • Kullanıcı Rolü: {user_role}")
        print(f"  • Senaryo: {scenario[:50]}...")
    
    def send_message(self, user_message: str, emotion_tag: Optional[str] = None) -> str:
        if not self.model:
            raise ValueError("❌ Senaryo ayarlanmamış! Önce set_scenario() çağır.")
        
        formatted_message = f"[{emotion_tag}] {user_message}" if emotion_tag else user_message
        
        self.chat_history.append({"role": "user", "parts": [formatted_message]})
        self.conversation_log.append({"speaker": "user", "text": user_message})
        
        try:
            response = self.model.generate_content(self.chat_history, stream=False)
            assistant_response = response.text
            
            self.chat_history.append({"role": "model", "parts": [assistant_response]})
            self.conversation_log.append({"speaker": "ai", "text": assistant_response})
            return assistant_response
            
        except Exception as e:
            print(f"❌ Gemini API Hatası: {str(e)}")
            raise Exception(f"API Bağlantı Hatası: {str(e)}")
    
    def send_message_stream(self, user_message: str, emotion_tag: Optional[str] = None):
        if not self.model:
            raise ValueError("❌ Senaryo ayarlanmamış! Önce set_scenario() çağır.")
        
        formatted_message = f"[{emotion_tag}] {user_message}" if emotion_tag else user_message
        self.chat_history.append({"role": "user", "parts": [formatted_message]})
        self.conversation_log.append({"speaker": "user", "text": user_message})
        
        try:
            response = self.model.generate_content(self.chat_history, stream=True)
            full_response = ""
            
            for chunk in response:
                try:
                    chunk_text = chunk.text
                    if chunk_text:
                        full_response += chunk_text
                        yield chunk_text
                except ValueError:
                    continue
            
            self.chat_history.append({"role": "model", "parts": [full_response]})
            self.conversation_log.append({"speaker": "ai", "text": full_response})
        
        except Exception as e:
            print(f"❌ Gemini API Hatası (Stream): {str(e)}")
            raise
    
    def evaluate_roleplay(self, evaluation_metrics: str):
        """Rol oynama konuşmasını değerlendir (streaming)"""
        if not self.model or not self.conversation_log:
            raise ValueError("❌ Değerlendirilecek konuşma yok!")
        
        self.chat_history.append({"role": "user", "parts": [evaluation_metrics]})
        
        try:
            response = self.model.generate_content(self.chat_history, stream=True)
            full_response = ""
            
            for chunk in response:
                try:
                    chunk_text = chunk.text
                    if chunk_text:
                        full_response += chunk_text
                        yield chunk_text
                except ValueError:
                    continue
            
            self.chat_history.append({"role": "model", "parts": [full_response]})
            self.conversation_log.append({"speaker": "evaluation", "text": full_response})
            
        except Exception as e:
            print(f"❌ Değerlendirme Hatası: {str(e)}")
            raise
    
    def get_conversation_log(self):
        """Konuşma kaydını döndür"""
        return self.conversation_log
    
    def get_chat_history(self) -> List[Dict]:
        return self.chat_history
    
    def clear_chat_history(self):
        """Mesaj geçmişini temizler"""
        self.chat_history = []
        self.conversation_log = []
        print("🔄 Chat history temizlendi")
    
    def reset(self):
        self.chat_history = []
        self.conversation_log = []
        self.scenario_context = None
        self.user_role = None
        self.ai_role = None
        self.model = None
        print("🔄 Gemini Client tamamen sıfırlandı")