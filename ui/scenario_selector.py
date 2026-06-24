"""
TimSen - Scenario Selector
Kullanıcının asistan seçmesi ve yeni asistan oluşturması için UI.
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QVBoxLayout, QLabel, QApplication, QFrame, 
    QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import QFont, QColor

# --- IMPORTLAR ---
from ui.widgets import CustomTitleBar, ModernButton
from ui.dialogs import ConfirmationDialog

# ---------------------------------------------------------
# ÖZEL SENARYO LİSTE ELEMANI (SATIR GÖRÜNÜMÜ)
# ---------------------------------------------------------
class ScenarioItem(QFrame):
    def __init__(self, name, file_path, select_callback, delete_callback):
        super().__init__()
        self.setFixedHeight(60) 
        
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #1f1f1f;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1px solid #333333;
                background-color: #0f0f0f;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 15, 0)
        layout.setSpacing(10)
        
        # Senaryo İsmi (Buton olarak)
        self.name_btn = QPushButton(name)
        self.name_btn.setCursor(Qt.PointingHandCursor)
        self.name_btn.clicked.connect(select_callback)
        self.name_btn.setSizePolicy(1, 1) 
        self.name_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #e0e0e0;
                border: none;
                text-align: left;
                font-family: 'SF Pro Display', 'Segoe UI';
                font-size: 14px;
                font-weight: 600;
                outline: none;
            }
            QPushButton:hover {
                color: #3b82f6;
            }
        """)
        layout.addWidget(self.name_btn)
        
        # Silme Butonu
        self.del_btn = QPushButton("✕")
        self.del_btn.setFixedSize(28, 28)
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(delete_callback)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #555;
                border: none;
                font-weight: bold;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 0.15);
                color: #ff3b30;
            }
        """)
        layout.addWidget(self.del_btn)

# ---------------------------------------------------------
# ANA PENCERE - ASISTAN SEÇİCİ
# ---------------------------------------------------------
class ScenarioSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(850, 500) 
        
        # Veri Yolları
        self.scenarios_path = "data/scenarios"
        if not os.path.exists(self.scenarios_path):
            os.makedirs(self.scenarios_path)
        
        self.setup_ui()
        self.load_scenarios() 

    def setup_ui(self):
        # Arka plan
        palette = self.palette()
        self.setAutoFillBackground(True)
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)

        # Ana Container
        self.main_container = QFrame(self)
        self.main_container.setStyleSheet("""
            QFrame#MainContainer {
                background-color: #0B0D13;
                border: 1px solid #333b4d;
                border-top: none;
                border-radius: 12px;
            }
        """)
        self.main_container.setObjectName("MainContainer")

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.main_container)

        content_layout = QVBoxLayout(self.main_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 1. BAŞLIK ÇUBUĞU
        self.title_bar = CustomTitleBar(self, title_text="Asistan Seçimi")
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #0F131A;
                border: none;
                border-bottom: 2px solid #2769ff;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        content_layout.addWidget(self.title_bar)

        # 2. İÇERİK (SPLIT VIEW)
        body_frame = QFrame()
        body_frame.setStyleSheet("background: transparent; border: none;")
        body_layout = QHBoxLayout(body_frame)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # --- SOL PANEL (SENARYO LİSTESİ) ---
        left_panel = QFrame()
        left_panel.setFixedWidth(340)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #0B0D13; 
                border-right: 1px solid #1f2430;
                border-bottom-left-radius: 12px;
                border-top: none;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(25, 30, 25, 30)
        left_layout.setSpacing(15)

        lbl_scenarios = QLabel("KAYITLI SENARYOLAR")
        lbl_scenarios.setStyleSheet("""
            color: #5d6675; 
            font-size: 11px; 
            font-weight: bold; 
            letter-spacing: 1px; 
            font-family: 'SF Pro Display', 'Segoe UI';
            border: none;
            background: transparent;
        """)
        left_layout.addWidget(lbl_scenarios)

        # Liste Widget
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                padding: 0px;
                margin-bottom: 10px; 
                border: none;
            }
            QListWidget::item:hover { background: transparent; }
            QListWidget::item:selected { background: transparent; }
            
            /* Scrollbar Stili */
            QScrollBar:vertical { background: #11141b; width: 6px; margin: 0px; }
            QScrollBar::handle:vertical { background: #333333; min-height: 20px; border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: #3b82f6; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        left_layout.addWidget(self.list_widget)

        # --- SAĞ PANEL (YENİ ASISTAN OLUŞTUR) ---
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background: qradialgradient(cx:0.5, cy:0, radius: 1, fx:0.5, fy:0, stop:0 #151525, stop:1 #000000);
                border-bottom-right-radius: 12px;
                border-top: none;
                border-left: none;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(20)

        right_layout.addStretch()

        # BÜYÜK + BUTONU
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(110, 110)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2769ff;
                color: white;
                font-size: 55px;
                font-weight: 300;
                border-radius: 55px;
                border: none;
                padding-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #3b7dff;
                border: 6px solid #1a1f29;
            }
            QPushButton:pressed {
                background-color: #1f5ccf;
                font-size: 52px;
            }
        """)
        self.add_btn.clicked.connect(self.handle_new_scenario)
        
        right_layout.addWidget(self.add_btn, alignment=Qt.AlignCenter)

        # Yazılar
        title_new = QLabel("Yeni Senaryo")
        title_new.setAlignment(Qt.AlignCenter)
        title_new.setStyleSheet("""
            color: white; 
            font-size: 22px; 
            font-weight: bold; 
            margin-top: 15px; 
            font-family: 'SF Pro Display', 'Segoe UI';
            border: none; 
            background: transparent;
        """)
        
        desc_new = QLabel("Kendi senaryonuzu tanımlayın")
        desc_new.setAlignment(Qt.AlignCenter)
        desc_new.setStyleSheet("""
            color: #666; 
            font-size: 14px; 
            font-family: 'SF Pro Display', 'Segoe UI';
            border: none; 
            background: transparent;
        """)

        right_layout.addWidget(title_new)
        right_layout.addWidget(desc_new)

        right_layout.addStretch()

        body_layout.addWidget(left_panel)
        body_layout.addWidget(right_panel, stretch=1)
        
        content_layout.addWidget(body_frame)

    def load_scenarios(self):
        """Kaydedilen senaryo JSON dosyalarını listele"""
        self.list_widget.clear()
        
        custom_files = [f for f in os.listdir(self.scenarios_path) if f.endswith('.json')]
        
        try:
            custom_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.scenarios_path, x)), reverse=True)
        except:
            pass

        for filename in custom_files:
            file_path = os.path.join(self.scenarios_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get("name", "Bilinmeyen Senaryo")
                    
                    list_item = QListWidgetItem(self.list_widget)
                    list_item.setSizeHint(QSize(0, 70))
                    
                    item_widget = ScenarioItem(
                        name=name, 
                        file_path=file_path,
                        select_callback=lambda _, p=file_path: self.handle_scenario_selection(p),
                        delete_callback=lambda _, f=filename, n=name: self.delete_scenario(f, n)
                    )
                    
                    self.list_widget.setItemWidget(list_item, item_widget)
                    
            except Exception as e:
                print(f"Hata: {filename} okunamadı. {e}")

    def delete_scenario(self, filename, scenario_name):
        """Senaryoyu siler"""
        dialog = ConfirmationDialog(
            title="Senaryoyu Sil",
            message=f"'{scenario_name}' adlı senaryoyu silmek istediğinize emin misiniz?",
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                os.remove(os.path.join(self.scenarios_path, filename))
                self.load_scenarios() 
            except Exception as e:
                print(f"Silme hatası: {e}")

    def handle_scenario_selection(self, file_path):
        """Senaryo seçilince ChatWindow açılır"""
        print(f"Seçilen Senaryo: {file_path}")
        
        from ui.chat_window import ChatWindow
        # scenario_path parametresi kullanılıyor (config_path değil)
        self.chat_window = ChatWindow(scenario_path=file_path)
        self.chat_window.show()
        self.close()

    def handle_new_scenario(self):
        """Yeni senaryo oluşturmak için ScenarioCreator aç"""
        try:
            from ui.scenario_creator import ScenarioCreatorUI
            self.creator = ScenarioCreatorUI()
            self.creator.show()
            self.close() 
        except ImportError as e:
            print(f"Hata: {e}")