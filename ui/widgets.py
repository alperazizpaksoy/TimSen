from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QLabel, QFrame, QHBoxLayout, QSizePolicy, QListView
)
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush

# ---------------------------------------------------------
# 1. PENCERE BAŞLIK ÇUBUĞU (DRAGGABLE)
# ---------------------------------------------------------
class CustomTitleBar(QFrame):
    def __init__(self, parent=None, title_text="Timur"):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(35)
        self.setStyleSheet("QFrame { background-color: #050505; border-bottom: 1px solid #1f1f1f; }")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        title_label = QLabel(title_text)
        title_label.setFont(QFont("SF Pro Display", 9, QFont.Bold))
        title_label.setStyleSheet("color: #888888; letter-spacing: 1px;")
        layout.addWidget(title_label)

        layout.addStretch()

        # Minimize Butonu
        btn_min = QPushButton("—")
        btn_min.setFixedSize(30, 30)
        btn_min.clicked.connect(self.parent.showMinimized)
        btn_min.setStyleSheet("""
            QPushButton { background: transparent; color: #a0a0a0; border: none; font-weight: bold; } 
            QPushButton:hover { background-color: #1f1f1f; color: white; }
        """)
        layout.addWidget(btn_min)

        # Kapat Butonu
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.parent.close)
        btn_close.setStyleSheet("""
            QPushButton { background: transparent; color: #a0a0a0; border: none; font-weight: bold; } 
            QPushButton:hover { background-color: #c42b1c; color: white; }
        """)
        layout.addWidget(btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.parent.oldPos:
            delta = event.globalPos() - self.parent.oldPos
            self.parent.move(self.parent.x() + delta.x(), self.parent.y() + delta.y())
            self.parent.oldPos = event.globalPos()


# ---------------------------------------------------------
# 2. MODERN TEMEL BİLEŞENLER (Button, Input, Combo vs.)
# ---------------------------------------------------------
class ModernButton(QPushButton):
    def __init__(self, text, primary=False):
        super().__init__(text)
        if primary:
            self.setStyleSheet("""
                QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #000000, stop:1 #3b82f6); color: white; border: 1px solid #3b82f6; border-radius: 12px; padding: 15px 32px; font-weight: 700; font-size: 14px; font-family: 'SF Pro Display', 'Segoe UI', sans-serif; letter-spacing: 0.5px; } 
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a1a1a, stop:1 #2563eb); border-color: #60a5fa; } 
                QPushButton:pressed { background: #000000; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton { background: #0f0f10; color: #a8b3cf; border: 1px solid #333333; border-radius: 12px; padding: 15px 32px; font-size: 14px; font-weight: 600; font-family: 'SF Pro Display', 'Segoe UI', sans-serif; } 
                QPushButton:hover { background: #1a1a1a; border-color: #555555; color: #ffffff; } 
                QPushButton:pressed { background: #000000; }
            """)

class ModernInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit { background: #0a0a0a; border: 1px solid #333333; border-radius: 8px; padding: 14px 18px; color: #ffffff; font-size: 14px; font-family: 'SF Pro Display', 'Segoe UI', sans-serif; selection-background-color: #3b82f6; } 
            QLineEdit:focus { border: 1px solid #3b82f6; background: #000000; } 
            QLineEdit:hover { border-color: #444444; }
        """)

class ModernTextEdit(QTextEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QTextEdit { background: #0a0a0a; border: 1px solid #333333; border-radius: 8px; padding: 14px 18px; color: #ffffff; font-size: 14px; font-family: 'SF Pro Display', 'Segoe UI', sans-serif; line-height: 1.6; selection-background-color: #3b82f6; } 
            QTextEdit:focus { border: 1px solid #3b82f6; background: #000000; }
        """)

class ModernComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setView(QListView())
        self.setStyleSheet("""
            QComboBox { background: #0a0a0a; border: 1px solid #333333; border-radius: 8px; padding: 14px 18px; color: #ffffff; font-size: 14px; font-family: 'SF Pro Display', 'Segoe UI', sans-serif; } 
            QComboBox:hover { border-color: #444444; background: #121212; } 
            QComboBox:focus { border: 1px solid #3b82f6; } 
            QComboBox::drop-down { border: none; width: 35px; } 
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 7px solid #3b82f6; margin-right: 12px; } 
            QComboBox QAbstractItemView { background-color: #050505; border: 1px solid #333333; selection-background-color: #3b82f6; color: #ffffff; outline: 0px; } 
            QComboBox QAbstractItemView::viewport { background-color: #050505; } 
            QScrollBar:vertical { border: none; background: #050505; width: 8px; margin: 0px; border-radius: 0px; } 
            QScrollBar::handle:vertical { background-color: #333333; min-height: 30px; border-radius: 4px; } 
            QScrollBar::handle:vertical:hover { background-color: #3b82f6; } 
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; } 
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

class SectionLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setFont(QFont("SF Pro Display", 10, QFont.Bold))
        self.setStyleSheet("color: #3b82f6; margin-top: 20px; margin-bottom: 8px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700;")


# ---------------------------------------------------------
# 3. TECH ICON (ÇİZİM İKONLAR: AYARLAR, KİLİT)
# ---------------------------------------------------------
class TechIconButton(QPushButton):
    def __init__(self, icon_type="settings", size=24, locked=False):
        super().__init__()
        self.setFixedSize(size + 10, size + 10)
        self.icon_type = icon_type
        self.is_hovered = False
        self.locked = locked 
        self.setCursor(Qt.PointingHandCursor if not locked else Qt.ArrowCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def enterEvent(self, event):
        if not self.locked: 
            self.is_hovered = True
            self.update() 

    def leaveEvent(self, event):
        if not self.locked:
            self.is_hovered = False
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        neon_blue = QColor("#3b82f6")
        dark_bg = QColor("#000000")
        passive_grey = QColor("#333333")
        
        if self.locked:
            pen_color = passive_grey
            brush_color = dark_bg 
            line_width = 2
        elif self.is_hovered:
            pen_color = dark_bg 
            brush_color = neon_blue 
            line_width = 2
        else:
            pen_color = neon_blue 
            brush_color = dark_bg 
            line_width = 1.5

        pen = QPen(pen_color)
        pen.setWidthF(line_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(brush_color))

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2

        if self.icon_type == "lock":
            body_w, body_h = 14, 11
            painter.drawRoundedRect(QRectF(cx - body_w/2, cy, body_w, body_h), 2, 2)
            shackle_w = 8
            shackle_h = 7
            painter.drawLine(int(cx - shackle_w/2), int(cy), int(cx - shackle_w/2), int(cy - shackle_h/2))
            painter.drawLine(int(cx + shackle_w/2), int(cy), int(cx + shackle_w/2), int(cy - shackle_h/2))
            painter.drawArc(int(cx - shackle_w/2), int(cy - shackle_h - 2), int(shackle_w), int(shackle_w), 0, 180 * 16)

        elif self.icon_type == "settings":
            radius = 7
            painter.drawEllipse(QPoint(int(cx), int(cy)), radius, radius)
            painter.setBrush(QBrush(pen_color if self.is_hovered else brush_color)) 
            for i in range(8):
                painter.save()
                painter.translate(cx, cy)
                painter.rotate(i * 45)
                painter.drawRect(-2, -radius - 3, 4, 3)
                painter.restore()
            painter.setBrush(QBrush(dark_bg if self.is_hovered else neon_blue)) 
            if not self.is_hovered:
                 painter.setBrush(QBrush(dark_bg)) 
            painter.drawEllipse(QPoint(int(cx), int(cy)), 3, 3)


# ---------------------------------------------------------
# 4. TEMPLATE ITEM (ŞABLON LİSTESİ + SİLME BUTONU)
# ---------------------------------------------------------
class TemplateItem(QFrame):
    def __init__(self, name, is_custom, apply_callback, delete_callback=None):
        super().__init__()
        self.setFixedHeight(50)
        
        # 1. Stil: Modül parçalarıyla aynı (#0a0a0a)
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #1f1f1f;
                border-radius: 8px;
            }
        """)
        
        # Ana Layout (Modül parçaları gibi yatay)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        # 2. İsim Butonu (Frame'in içinde şeffaf duracak)
        self.main_btn = QPushButton(name)
        self.main_btn.setCursor(Qt.PointingHandCursor)
        self.main_btn.clicked.connect(apply_callback)
        self.main_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Sadece yazı mavi olsun, border yok
        self.main_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888888;
                border: none;
                text-align: left;
                font-family: 'SF Pro Display', 'Segoe UI';
                font-size: 13px;
                outline: none;
            }
            QPushButton:hover {
                color: #3b82f6; /* Sadece yazıyı Mavi yap */
            }
        """)
        layout.addWidget(self.main_btn)
        
        # 3. Silme Butonu
        if is_custom and delete_callback:
            self.del_btn = QPushButton("✕")
            self.del_btn.setFixedSize(24, 24)
            self.del_btn.setCursor(Qt.PointingHandCursor)
            self.del_btn.clicked.connect(delete_callback)
            
            # Modüldeki silme butonunun AYNISI
            self.del_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #555555;
                    border: none;
                    font-weight: bold;
                    border-radius: 4px;
                    outline: none;
                }
                QPushButton:hover {
                    background: rgba(255, 59, 48, 0.1); 
                    color: #ff3b30;
                }
            """)
            layout.addWidget(self.del_btn)