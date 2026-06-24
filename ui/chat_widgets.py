from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
                             QGraphicsOpacityEffect, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter, QPainterPath, QFontMetrics, QTextDocument, QTextOption
import os


class MessageBubble(QFrame):
    """
    Sohbet balonlarını oluşturan görsel sınıf (Streaming ve dinamik boyutlandırma destekli).
    """
    def __init__(self, text, is_user=True, avatar_path=None):
        super().__init__()
        self.text = text
        self.is_user = is_user
        self.avatar_path = avatar_path
        self.opacity_value = 0.0

        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background: transparent; border: none;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 8, 15, 8)
        main_layout.setSpacing(12)

        # AVATAR BLOĞU (Sadece Asistan)
        if not self.is_user:
            avatar_size = 35
            self.avatar_lbl = QLabel()
            self.avatar_lbl.setFixedSize(avatar_size, avatar_size)

            if self.avatar_path and os.path.exists(self.avatar_path):
                pixmap = QPixmap(self.avatar_path).scaled(
                    avatar_size, avatar_size, 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            else:
                pixmap = QPixmap(avatar_size, avatar_size)
                pixmap.fill(Qt.transparent)

            if not pixmap.isNull():
                rounded = QPixmap(avatar_size, avatar_size)
                rounded.fill(Qt.transparent)
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                path = QPainterPath()
                path.addEllipse(0, 0, avatar_size, avatar_size)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                pixmap = rounded

            self.avatar_lbl.setPixmap(pixmap)
            self.avatar_lbl.setStyleSheet("border: none; border-radius: 17px;")
            main_layout.addWidget(self.avatar_lbl, 0, Qt.AlignTop)

        # MESAJ BALONU (QTextEdit)
        self.message_widget = QTextEdit()
        self.message_widget.setPlainText(self.text)
        self.message_widget.setReadOnly(True)
        self.message_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_widget.setFont(QFont("Arial", 10))
        self.message_widget.setWordWrapMode(QTextOption.WordWrap)
        
        # HATA BURADAYDI: Qt.AlignCenter yerine Qt.AlignLeft kullandık (Sola yaslama)
        self.message_widget.setAlignment(Qt.AlignLeft)  
        
        self.message_widget.setFrameStyle(0)

        # Boyutu hesapla ve ayarla
        self.calculate_size()

        if self.is_user:
            self.message_widget.setStyleSheet("""
                QTextEdit {
                    background-color: #2e8bff;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 18px;
                    border: none;
                }
            """)
            main_layout.addStretch()
            main_layout.addWidget(self.message_widget, 0, Qt.AlignTop)
        else:
            self.message_widget.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    padding: 10px 15px;
                    border-radius: 18px;
                    border: 1px solid #404040;
                }
            """)
            main_layout.addWidget(self.message_widget, 0, Qt.AlignTop)
            main_layout.addStretch()

        # Animasyon Ayarları
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def calculate_size(self):
        """Asil_chat mantığıyla kusursuz boyut hesaplama"""
        font = self.message_widget.font()
        font_metrics = QFontMetrics(font)
        
        # Boyut sınırları
        min_width = 80
        max_width = 650
        text_padding = 40  
        safety_margin = 10  
        
        text = self.message_widget.toPlainText()
        if not text.strip():
            text = "x"
            
        lines = text.split('\n')
        max_line_width = 0
        
        for line in lines:
            words = line.split()
            if words:
                line_width = 0
                for i, word in enumerate(words):
                    line_width += font_metrics.horizontalAdvance(word)
                    if i < len(words) - 1:
                        line_width += font_metrics.horizontalAdvance(' ')
                max_line_width = max(max_line_width, line_width)
            else:
                max_line_width = max(max_line_width, 0)
        
        total_width = max_line_width + text_padding
        
        if total_width < min_width:
            width = min_width
        elif total_width > max_width:
            width = max_width
        else:
            width = total_width
        
        # Yükseklik hesaplaması
        doc = QTextDocument()
        doc.setDefaultFont(font)
        doc.setPlainText(text)
        doc.setTextWidth(width + safety_margin - text_padding)
        actual_height = doc.size().height()
        
        line_count = len(lines)
        if line_count == 1 and not any(line.strip() == '' for line in lines):
            padding = 16 
            min_height = 38 
        else:
            padding = 22
            min_height = 45
        
        final_height = max(actual_height + padding, min_height)
        self.message_widget.setFixedSize(int(width + safety_margin), int(final_height))

    def update_message(self, new_text):
        """Mesajı güncelle ve yeniden boyutlandır (Streaming için)"""
        self.text = new_text
        self.message_widget.setPlainText(self.text)
        
        # DÜZELTME: Streaming sırasında da metin güncellendiğinde sola yaslı kalsın
        self.message_widget.setAlignment(Qt.AlignLeft)
        
        self.calculate_size()
        
    def update_text(self, new_text):
        """Eski koddaki isimlendirme çakışmalarını önlemek için alias"""
        self.update_message(new_text)

    def animate_in(self):
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    @pyqtProperty(float)
    def opacity(self):
        return self.opacity_value
    
    @opacity.setter
    def opacity(self, value):
        self.opacity_value = value
        self.setWindowOpacity(value)