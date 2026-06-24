"""
TimSen - Chat Window
Gemini'ye bağlı, senaryo tabanlı sohbet penceresi (Streaming Destekli)
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QScrollArea, QApplication, QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, QEvent, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPixmap, QIcon, QTextOption

# --- IMPORTLAR ---
from ui.widgets import CustomTitleBar
from ui.chat_widgets import MessageBubble
from llm.gemini_client import GeminiClient
from ui.custom_messagebox import show_warning, show_info, show_error, show_question

try:
    from config import ICON_PATH, ICON_PATH_RIGHT, ICON_ICO
except ImportError:
    ICON_PATH = "assets/YanTimur.png"
    ICON_ICO = "assets/Timur.ico"


class ScenarioLoaderThread(QThread):
    """Gemini Client'ı arka planda yükle"""
    ready = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, scenario_data, is_roleplay=False, user_role=None, ai_role=None):
        super().__init__()
        self.scenario_data = scenario_data
        self.is_roleplay = is_roleplay
        self.user_role = user_role
        self.ai_role = ai_role

    def run(self):
        try:
            print("🔄 Senaryo yükleniyor... Gemini Client başlatılıyor")
            gemini = GeminiClient()

            if self.is_roleplay:
                # Role-play modu
                gemini.init_roleplay(
                    user_role=self.user_role,
                    ai_role=self.ai_role,
                    scenario=self.scenario_data.get("scenario", "")
                )
            else:
                # Normal chat modu
                scenario_description = self.scenario_data.get("scenario", "")
                if not scenario_description:
                    scenario_description = f"{self.scenario_data.get('name', 'Senaryo')} - {self.scenario_data.get('description', '')}"
                gemini.set_scenario(scenario_description)

            self.ready.emit(gemini)

        except Exception as e:
            self.error.emit(f"❌ Yükleme hatası: {str(e)}")


class GeminiStreamingWorker(QThread):
    """Gemini'den kelime kelime (stream) cevap al"""
    chunk_received = pyqtSignal(str, str)  # chunk_text, full_response_so_far
    finished = pyqtSignal(str)             # final_response
    error = pyqtSignal(str)

    def __init__(self, gemini_client, user_message, emotion_tag):
        super().__init__()
        self.gemini_client = gemini_client
        self.user_message = user_message
        self.emotion_tag = emotion_tag

    def run(self):
        try:
            full_response = ""
            for chunk in self.gemini_client.send_message_stream(self.user_message, self.emotion_tag):
                full_response += chunk
                self.chunk_received.emit(chunk, full_response)

            self.finished.emit(full_response)
        except Exception as e:
            self.error.emit(str(e))


class ChatWindow(QWidget):
    closed_signal = pyqtSignal()

    def __init__(self, scenario_path=None, parent=None):
        super().__init__()
        self.parent_overlay = parent
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setFixedSize(900, 750)
        self.setWindowIcon(QIcon(ICON_ICO))

        self.scenario_path = scenario_path
        self.scenario_name = "TimSen Chat"
        self.scenario_data = {}
        self.avatar_path = ICON_PATH

        self.gemini_client = None

        # UI Durumu ve Stream Değişkenleri
        self.is_waiting_response = False
        self.current_response_bubble = None
        self.response_worker = None
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.update_thinking_animation)
        self.thinking_dots = 0
        self.thinking_bubble = None

        # Role-play modu
        self.is_roleplay_mode = False
        self.user_role = None
        self.ai_role = None
        self.evaluation_metrics = None

        # Konuşma kaydı
        self.base_data_path = "data"
        self.conversations_path = os.path.join(self.base_data_path, "conversations")
        if not os.path.exists(self.conversations_path):
            os.makedirs(self.conversations_path)

        if scenario_path:
            self.load_scenario(scenario_path)

        self.setup_ui()
        self.start_loading_scenario()

    def load_scenario(self, scenario_path):
        try:
            with open(scenario_path, "r", encoding="utf-8") as f:
                self.scenario_data = json.load(f)
                self.scenario_name = self.scenario_data.get("name", "TimSen Chat")

                # Role-play özellikleri kontrol et
                if "user_role" in self.scenario_data and "ai_role" in self.scenario_data:
                    self.is_roleplay_mode = True
                    self.user_role = self.scenario_data.get("user_role")
                    self.ai_role = self.scenario_data.get("ai_role")
                    self.evaluation_metrics = self.scenario_data.get("evaluation_metrics", "")

                if "avatar" in self.scenario_data and os.path.exists(self.scenario_data["avatar"]):
                    self.avatar_path = self.scenario_data["avatar"]
        except Exception as e:
            print(f"⚠️ Senaryo yükleme hatası: {e}")

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qradialgradient(cx:0.5, cy:0, radius: 1, fx:0.5, fy:0, stop:0 #151525, stop:1 #000000);
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #0B0D13; width: 8px; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #333333; border-radius: 4px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #2769ff; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title_text=self.scenario_name)
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet("""
            QFrame { background-color: #0F131A; border-bottom: 2px solid #2769ff; }
            QLabel { color: #2769ff; font-weight: bold; font-size: 14px; }
        """)
        self.main_layout.addWidget(self.title_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_content = QWidget()
        self.chat_content.setStyleSheet("background: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setContentsMargins(0, 10, 0, 10)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_content)
        self.main_layout.addWidget(self.scroll_area)

        self.create_input_area()

        self.loading_overlay = QFrame(self)
        self.loading_overlay.setGeometry(0, 50, 900, 700)
        self.loading_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.95);")

        l_layout = QVBoxLayout(self.loading_overlay)
        l_layout.setAlignment(Qt.AlignCenter)

        self.loading_label = QLabel(f"{self.scenario_name} Hazırlanıyor...")
        self.loading_label.setStyleSheet("color: #2769ff; font-size: 18px; font-weight: bold;")
        l_layout.addWidget(self.loading_label)

    def create_input_area(self):
        self.input_container = QFrame()
        self.input_container.setFixedHeight(80)
        self.input_container.setStyleSheet(
            "QFrame { background-color: #0B0D13; border-top: 1px solid #1f1f1f; }"
        )

        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)
        input_layout.setAlignment(Qt.AlignBottom)

        # --- QTextEdit (dinamik yükseklik) ---
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Mesajınızı yazın...")
        self.input_field.setMinimumHeight(45)
        self.input_field.setMaximumHeight(120)
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_field.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #151922;
                border: 1px solid #2b3242;
                border-radius: 22px;
                padding: 12px 20px;
                font-size: 14px;
                color: #ffffff;
            }
            QTextEdit:focus {
                border: 1px solid #2769ff;
                background-color: #1a1e29;
            }
        """)
        # Enter tuşunu yakala
        self.input_field.installEventFilter(self)
        # İçerik değişince yüksekliği güncelle
        self.input_field.document().contentsChanged.connect(self.adjust_input_height)

        # --- Gönder Butonu ---
        self.send_button = QPushButton("➤")
        self.send_button.setFixedSize(45, 45)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2769ff; color: white; border: none;
                border-radius: 22px; font-size: 20px;
                padding-bottom: 2px; padding-left: 2px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3b7dff; }
            QPushButton:pressed { background-color: #1f5ccf; }
        """)

        # --- Rol Oyunu Bitir Butonu ---
        self.finish_button = QPushButton("Değerlendir")
        self.finish_button.setFixedSize(150, 45)
        self.finish_button.setCursor(Qt.PointingHandCursor)
        self.finish_button.clicked.connect(self.finish_roleplay)
        self.finish_button.setStyleSheet("""
            QPushButton {
                background-color: #2769ff; color: white; border: none;
                border-radius: 8px; font-size: 11px; font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover { background-color: #3b7dff; }
            QPushButton:pressed { background-color: #1f5ccf; }
        """)
        self.finish_button.hide()

        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.finish_button)
        self.main_layout.addWidget(self.input_container)

    # ------------------------------------------------------------------
    # Dinamik yükseklik ayarı
    # ------------------------------------------------------------------
    def adjust_input_height(self):
        """Yazılan metin arttıkça input alanını ve container'ı büyüt."""
        doc_height = self.input_field.document().size().height()
        # En az 45px, en fazla 120px (yaklaşık 4 satır)
        new_field_height = max(45, min(int(doc_height) + 24, 120))
        self.input_field.setFixedHeight(new_field_height)

        # Container da buna göre büyüsün (üst+alt padding = 30px)
        new_container_height = new_field_height + 35
        self.input_container.setFixedHeight(new_container_height)

    # ------------------------------------------------------------------
    # Enter = gönder | Shift+Enter = yeni satır
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.input_field and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if event.modifiers() & Qt.ShiftModifier:
                    # Shift+Enter → normal yeni satır, olayı geçir
                    return False
                else:
                    # Sadece Enter → mesaj gönder
                    self.send_message()
                    return True  # Olayı yut
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Senaryo yükleme
    # ------------------------------------------------------------------
    def start_loading_scenario(self):
        self.loader = ScenarioLoaderThread(
            self.scenario_data,
            is_roleplay=self.is_roleplay_mode,
            user_role=self.user_role,
            ai_role=self.ai_role
        )
        self.loader.ready.connect(self.on_scenario_loaded)
        self.loader.error.connect(self.on_loading_error)
        self.loader.start()

    def on_scenario_loaded(self, gemini_client):
        self.gemini_client = gemini_client

        if self.is_roleplay_mode:
            self.finish_button.show()
            print(f"🎭 Role-play modu aktif: {self.ai_role} vs {self.user_role}")

        print(f"✅ {self.scenario_name} hazır!")
        self.loading_overlay.hide()
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

        if self.is_roleplay_mode:
            first_msg = f"Merhaba! Ben {self.ai_role}. {self.scenario_data.get('scenario', 'Lütfen devam edin.')}"
        else:
            first_msg = f"Merhaba! Ben {self.scenario_name}. Nasıl yardımcı olabilirim?"

        self.add_message_bubble(first_msg, is_user=False)

    def on_loading_error(self, error_msg):
        print(f"❌ {error_msg}")
        self.loading_label.setText(f"Hata: {error_msg}")
        show_error(self, "Hata", error_msg)

    # ------------------------------------------------------------------
    # Mesaj baloncukları
    # ------------------------------------------------------------------
    def add_message_bubble(self, text, is_user=True):
        bubble = MessageBubble(text, is_user=is_user, avatar_path=self.avatar_path)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        bubble.animate_in()
        QTimer.singleShot(100, self.scroll_to_bottom)

    # ------------------------------------------------------------------
    # Mesaj gönderme
    # ------------------------------------------------------------------
    def send_message(self):
        if self.is_waiting_response or not self.gemini_client:
            return

        message = self.input_field.toPlainText().strip()
        if not message:
            return

        self.add_message_bubble(message, is_user=True)
        self.input_field.clear()          # clear() QTextEdit'te de çalışır
        # clear() sonrası adjust_input_height otomatik tetiklenir; container küçülür

        self.is_waiting_response = True
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.start_thinking_animation()

        self.response_worker = GeminiStreamingWorker(self.gemini_client, message, None)
        self.response_worker.chunk_received.connect(self.on_chunk_received)
        self.response_worker.finished.connect(self.on_response_finished)
        self.response_worker.error.connect(self.on_response_error)
        self.response_worker.start()

    # ------------------------------------------------------------------
    # Düşünme animasyonu
    # ------------------------------------------------------------------
    def start_thinking_animation(self):
        self.thinking_bubble = MessageBubble("●○○", is_user=False, avatar_path=self.avatar_path)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.thinking_bubble)
        self.thinking_bubble.animate_in()
        self.thinking_dots = 0
        self.thinking_timer.start(500)
        self.scroll_to_bottom()

    def update_thinking_animation(self):
        if self.thinking_bubble:
            self.thinking_dots = (self.thinking_dots + 1) % 4
            txt = ["●○○", "○●○", "○○●", "○●○"][self.thinking_dots % 3]
            self.thinking_bubble.update_message(txt)

    def stop_thinking_animation(self):
        self.thinking_timer.stop()
        if self.thinking_bubble:
            self.thinking_bubble.setParent(None)
            self.thinking_bubble.deleteLater()
            self.thinking_bubble = None

    # ------------------------------------------------------------------
    # Streaming geri çağrıları
    # ------------------------------------------------------------------
    def on_chunk_received(self, chunk, full_response):
        if not self.current_response_bubble:
            self.stop_thinking_animation()
            self.current_response_bubble = MessageBubble("", is_user=False, avatar_path=self.avatar_path)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.current_response_bubble)
            self.current_response_bubble.animate_in()

        if self.current_response_bubble:
            self.current_response_bubble.update_message(full_response)
            self.scroll_to_bottom()

    def on_response_finished(self, final_response):
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.is_waiting_response = False
        self.input_field.setFocus()

        self.current_response_bubble = None
        self.scroll_to_bottom()

        if self.response_worker:
            self.response_worker.deleteLater()
            self.response_worker = None

    def on_response_error(self, error_msg):
        self.stop_thinking_animation()

        if not self.current_response_bubble:
            self.current_response_bubble = MessageBubble(
                f"❌ Hata: {error_msg}", is_user=False, avatar_path=self.avatar_path
            )
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.current_response_bubble)
            self.current_response_bubble.animate_in()
        else:
            self.current_response_bubble.update_message(f"❌ Hata: {error_msg}")

        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.is_waiting_response = False
        self.current_response_bubble = None
        self.scroll_to_bottom()

    # ------------------------------------------------------------------
    # Yardımcılar
    # ------------------------------------------------------------------
    def scroll_to_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        QTimer.singleShot(10, lambda: sb.setValue(sb.maximum()))

    # ------------------------------------------------------------------
    # Rol oyunu tamamlama
    # ------------------------------------------------------------------
    def finish_roleplay(self):
        if not self.evaluation_metrics:
            show_warning(self, "Eksik Veri", "Değerlendirme metrikleri tanımlanmamış!")
            return

        if not show_question(self, "Rol Oyunmasını Bitir",
                             "Rol oyunmasını bitirmek ve değerlendirme almak istediğinize emin misiniz?"):
            return

        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.finish_button.setEnabled(False)

        self.start_thinking_animation()

        self.response_worker = GeminiStreamingWorker(self.gemini_client, self.evaluation_metrics, None)
        self.response_worker.chunk_received.connect(self.on_evaluation_chunk)
        self.response_worker.finished.connect(self.on_evaluation_finished)
        self.response_worker.error.connect(self.on_response_error)
        self.response_worker.start()

    def on_evaluation_chunk(self, chunk, full_response):
        if not self.current_response_bubble:
            self.stop_thinking_animation()
            self.current_response_bubble = MessageBubble(
                "📊 DEĞERLENDİRME:\n\n", is_user=False, avatar_path=self.avatar_path
            )
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.current_response_bubble)
            self.current_response_bubble.animate_in()

        if self.current_response_bubble:
            self.current_response_bubble.update_message("📊 DEĞERLENDİRME:\n\n" + full_response)
            self.scroll_to_bottom()

    def on_evaluation_finished(self, final_response):
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.finish_button.setEnabled(False)

        self.save_conversation(final_response)

        self.current_response_bubble = None
        self.scroll_to_bottom()

        show_info(self, "Tamamlandı", "Rol oyunması tamamlandı ve kaydedildi!")

    def save_conversation(self, evaluation):
        try:
            scenario_slug = self.scenario_data.get('name', 'scenario').lower().replace(" ", "-")
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{scenario_slug}_{timestamp}.json"
            filepath = os.path.join(self.conversations_path, filename)

            conversation = self.gemini_client.get_conversation_log()

            data = {
                "scenario_name": self.scenario_data.get('name', ''),
                "user_role": self.user_role or self.scenario_data.get('user_role', ''),
                "ai_role": self.ai_role or self.scenario_data.get('ai_role', ''),
                "evaluation_metrics": self.evaluation_metrics or self.scenario_data.get('evaluation_metrics', ''),
                "created_at": datetime.now().isoformat(),
                "conversation": conversation,
                "evaluation_report": evaluation
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ Konuşma kaydedildi: {filepath}")

        except Exception as e:
            print(f"❌ Kayıt hatası: {str(e)}")
            show_error(self, "Kayıt Hatası", f"Konuşma kaydedilirken hata: {str(e)}")

    # ------------------------------------------------------------------
    # Pencere kapatma
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        if self.thinking_timer.isActive():
            self.thinking_timer.stop()

        if self.response_worker and self.response_worker.isRunning():
            self.response_worker.terminate()

        self.closed_signal.emit()

        from ui.scenario_selector import ScenarioSelector
        self.selector = ScenarioSelector()
        self.selector.show()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())