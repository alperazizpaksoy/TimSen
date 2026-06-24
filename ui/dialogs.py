from PyQt5.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QListView
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QFont
from ui.widgets import ModernInput, ModernComboBox, ModernButton

# --- 1. VERİ GİRİŞ PENCERESİ (MODÜL EKLEME VB.) ---
class CustomInputDialog(QDialog):
    def __init__(self, title, label_text, placeholder=None, items=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 220)
        self.input_text = None
        self.items = items 
        self.oldPos = None
        self.setup_ui(title, label_text, placeholder)

    def setup_ui(self, title, label_text, placeholder):
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(0, 0, 400, 220)
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: #0B0D13;
                border: 1px solid #1f1f1f; 
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Başlık
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #0F131A;
                border-bottom: 1px solid #1f1f1f;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                background: transparent;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; border: none;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: #888; border: none; font-weight: bold; } QPushButton:hover { color: #ff3b30; }")

        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)

        # İçerik
        content_area = QWidget()
        content_area.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(15)

        lbl_info = QLabel(label_text)
        lbl_info.setStyleSheet("color: #a0a0a0; font-family: 'Segoe UI'; font-size: 13px; border: none;")
        content_layout.addWidget(lbl_info)

        # Giriş Alanı
        if self.items:
            self.input_widget = ModernComboBox()
            self.input_widget.setView(QListView())
            self.input_widget.addItems(self.items)
            self.input_widget.setStyleSheet("""
                QComboBox {
                    background-color: #151922;
                    border: 1px solid #2b3242;
                    border-radius: 6px;
                    padding: 10px;
                    color: white;
                    font-size: 14px;
                    font-family: 'Segoe UI', sans-serif;
                }
                QComboBox:hover { border-color: #3b82f6; }
                QComboBox:focus { border: 1px solid #3b82f6; }
                QComboBox::drop-down { border: none; width: 30px; }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #3b82f6;
                    margin-right: 10px;
                }
                QComboBox QAbstractItemView {
                    background-color: #0B0D13;
                    border: 1px solid #333;
                    border-radius: 4px;
                    selection-background-color: #3b82f6;
                    selection-color: white;
                    color: white;
                    outline: none;
                    padding: 0px;
                    margin: 0px;
                }
                QComboBox QAbstractItemView::item {
                    background-color: #0B0D13;
                    color: white;
                    padding: 8px 12px;
                    border: none;
                    margin: 0px;
                }
                QComboBox QAbstractItemView::item:hover { background-color: #1a1d28; }
                QComboBox QAbstractItemView::item:selected { background-color: #3b82f6; color: white; }
                QScrollBar:vertical { border: none; background: #0B0D13; width: 8px; margin: 0px; }
                QScrollBar::handle:vertical { background-color: #333333; min-height: 30px; border-radius: 4px; }
                QScrollBar::handle:vertical:hover { background-color: #3b82f6; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: #0B0D13; }
            """)
        else:
            self.input_widget = ModernInput(placeholder if placeholder else "")
            self.input_widget.setStyleSheet("""
                QLineEdit {
                    background: #151922;
                    border: 1px solid #2b3242;
                    border-radius: 6px;
                    padding: 10px;
                    color: white;
                    font-size: 14px;
                }
                QLineEdit:focus { border: 1px solid #3b82f6; }
            """)
            
        content_layout.addWidget(self.input_widget)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedSize(80, 32)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("QPushButton { background: transparent; color: #888; border: 1px solid #333; border-radius: 6px; } QPushButton:hover { color: white; border-color: #3b82f6; }")

        btn_add = QPushButton("Ekle") 
        btn_add.setFixedSize(80, 32)
        btn_add.clicked.connect(self.validate_and_accept)
        btn_add.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 6px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }")

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_add)
        content_layout.addLayout(btn_layout)
        layout.addWidget(content_area)

        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent

    def validate_and_accept(self):
        if self.items:
            text = self.input_widget.currentText()
        else:
            text = self.input_widget.text().strip()
        if text:
            self.input_text = text
            self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.oldPos = event.globalPos()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

# --- 2. SİLME ONAY PENCERESİ (MEVCUT) ---
class ConfirmationDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(380, 180)
        self.oldPos = None
        self.setup_ui(title, message)

    def setup_ui(self, title, message):
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(0, 0, 380, 180)
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: #0B0D13;
                border: 1px solid #1f1f1f;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #0F131A;
                border-bottom: 1px solid #1f1f1f;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                background: transparent;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; border: none;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: #888; border: none; font-weight: bold; } QPushButton:hover { color: #ff3b30; }")

        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)

        content_area = QWidget()
        content_area.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(20)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #e0e0e0; font-family: 'Segoe UI'; font-size: 14px; border: none;")
        content_layout.addWidget(msg_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_no = QPushButton("Hayır")
        btn_no.setFixedSize(80, 32)
        btn_no.clicked.connect(self.reject)
        btn_no.setCursor(Qt.PointingHandCursor)
        btn_no.setStyleSheet("QPushButton { background: transparent; color: #aaa; border: 1px solid #444; border-radius: 6px; } QPushButton:hover { color: white; border-color: #3b82f6; background-color: rgba(59, 130, 246, 0.1); }")

        btn_yes = QPushButton("Evet, Sil")
        btn_yes.setFixedSize(90, 32)
        btn_yes.setCursor(Qt.PointingHandCursor)
        btn_yes.clicked.connect(self.accept)
        btn_yes.setStyleSheet("QPushButton { background-color: rgba(255, 59, 48, 0.1); color: #ff3b30; border: 1px solid #ff3b30; border-radius: 6px; font-weight: bold; } QPushButton:hover { background-color: #ff3b30; color: white; }")

        btn_layout.addWidget(btn_no)
        btn_layout.addWidget(btn_yes)
        content_layout.addLayout(btn_layout)
        layout.addWidget(content_area)

        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.oldPos = event.globalPos()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

# --- 3. İNDİRME ONAY PENCERESİ (YENİ - MAVİ/SİYAH BUTONLU) ---
class CustomConfirmDialog(QDialog):
    def __init__(self, title, message, info_details=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 250)
        self.oldPos = None
        self.setup_ui(title, message, info_details)

    def setup_ui(self, title, message, info_details):
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(0, 0, 400, 250)
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: #0B0D13;
                border: 1px solid #1f1f1f;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Başlık
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #0F131A;
                border-bottom: 1px solid #1f1f1f;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                background: transparent;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; border: none;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: #888; border: none; font-weight: bold; } QPushButton:hover { color: #ff3b30; }")

        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)

        # İçerik
        content_area = QWidget()
        content_area.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(15)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #cccccc; font-size: 14px; line-height: 1.4; border: none;")
        content_layout.addWidget(msg_lbl)

        # Detay Kutusu (Model boyutu)
        if info_details:
            details_frame = QFrame()
            details_frame.setStyleSheet("""
                QFrame {
                    background-color: #151922;
                    border: 1px dashed #333;
                    border-radius: 6px;
                    padding: 5px;
                }
            """)
            det_layout = QVBoxLayout(details_frame)
            det_layout.setContentsMargins(10, 10, 10, 10)
            
            det_lbl = QLabel(info_details)
            det_lbl.setStyleSheet("color: #3b82f6; font-family: monospace; font-size: 12px; border: none;")
            det_layout.addWidget(det_lbl)
            
            content_layout.addWidget(details_frame)
            
        # --- BUTONLAR (İSTEĞİNE GÖRE TASARLANDI) ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # İPTAL ET (Siyah/Gri Şeffaf - CustomInputDialog gibi)
        btn_cancel = QPushButton("İptal Et")
        btn_cancel.setFixedSize(80, 32)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("QPushButton { background: transparent; color: #888; border: 1px solid #333; border-radius: 6px; } QPushButton:hover { color: white; border-color: #3b82f6; }")

        # DEVAM ET (Mavi Dolgulu - CustomInputDialog gibi)
        btn_ok = QPushButton("Devam Et")
        btn_ok.setFixedSize(100, 32)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 6px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }")
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        content_layout.addLayout(btn_layout)
        
        layout.addWidget(content_area)

        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.oldPos = event.globalPos()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()