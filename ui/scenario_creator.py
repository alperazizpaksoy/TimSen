import sys
import json
import os
import uuid
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QApplication,
    QPushButton, QScrollArea, QFileDialog, QDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QFont, QPixmap

# --- IMPORTLAR ---
from ui.widgets import (
    CustomTitleBar, ModernButton, ModernInput, ModernTextEdit, 
    SectionLabel, TemplateItem
)
from ui.dialogs import CustomInputDialog, CustomConfirmDialog

# --- SEÇİM KARTI ---
class SelectionCard(QFrame):
    """Seçim kartı - Seslendirici, Ton vb seçim için"""
    from PyQt5.QtCore import pyqtSignal
    clicked = pyqtSignal(object)

    def __init__(self, value_id, title, parent=None):
        super().__init__(parent)
        self.value_id = value_id
        self.is_selected = False
        
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50) 
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.title_lbl)
        layout.addStretch() 

        self.update_style()

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        font_family = "'SF Pro Display', 'Segoe UI'"
        
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #0a0a0a;
                    border: 1px solid #3b82f6; 
                    border-radius: 8px;
                }
            """)
            self.title_lbl.setStyleSheet(f"""
                color: #3b82f6; 
                font-family: {font_family};
                font-size: 13px;
                font-weight: bold;
                border: none;
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #0a0a0a;
                    border: 1px solid #1f1f1f;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border: 1px solid #3b82f6;
                }
            """)
            self.title_lbl.setStyleSheet(f"""
                color: #888888;
                font-family: {font_family};
                font-size: 13px;
                font-weight: normal;
                border: none;
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.value_id)
            super().mousePressEvent(event)

# --- ASISTAN OLUŞTUR PENCERESI ---
class ScenarioCreatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(1550, 850)
        self.oldPos = None
        self.default_avatar_path = "assets/YanTimur.png"
        
        self.base_data_path = "data"
        self.scenarios_path = os.path.join(self.base_data_path, "scenarios")
        
        if not os.path.exists(self.base_data_path): os.makedirs(self.base_data_path)
        if not os.path.exists(self.scenarios_path): os.makedirs(self.scenarios_path)
            
        self.templates_file = os.path.join(self.base_data_path, "templates.json")
        self.templates_data = self.load_templates()
        
        # Seçim Grupları
        self.voice_cards = {}
        
        # Degerlendirme Metrikleri
        self.evaluation_metrics_input = None
        self.evaluation_template_layout = None
        
        # Template Layouts
        self.scenario_template_layout = None
        
        # Asistan inputları
        self.scenario_input = None
        self.desc_input = None
        self.scenario_name_input = None
        self.avatar_upload_label = None
        
        self.setup_ui()

    def load_templates(self):
        defaults = {
            "professional": {"name": "Profesyonel", "description": "Profesyonel asistan"},
        }
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except: pass
        return defaults

    def get_evaluation_templates(self):
        """Değerlendirme metriklerini templates'den ayıkla"""
        result = {}
        for key, data in self.templates_data.items():
            if "evaluation_metrics" in data:
                result[key] = data
        return result

    def setup_ui(self):
        palette = self.palette()
        self.setAutoFillBackground(True)
        palette.setColor(QPalette.Window, QColor(0, 0, 0)) 
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.title_bar = CustomTitleBar(self, title_text="TimSen - Asistan Oluştur")
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.create_header())

        content = QWidget()
        content.setStyleSheet("QWidget { background: qradialgradient(cx:0.5, cy:0, radius: 1, fx:0.5, fy:0, stop:0 #151525, stop:1 #000000); }")
        
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(40)
        content.setLayout(content_layout)

        content_layout.addWidget(self.create_general_settings(), 1)
        content_layout.addWidget(self.create_evaluation(), 1)
        content_layout.addWidget(self.create_scenario_display(), 1)

        main_layout.addWidget(content)

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(110)
        header.setStyleSheet("QFrame { background: #000000; border: none; }")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(35, 25, 35, 10) 
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Yeni Asistan")
        title.setFont(QFont("SF Pro Display", 26, QFont.Bold))
        title.setStyleSheet("color: #ffffff; font-weight: 800;")
        
        subtitle = QLabel("Kişiselleştirilmiş AI asistan oluştur ve yapılandır")
        subtitle.setFont(QFont("SF Pro Display", 13))
        subtitle.setStyleSheet("color: #666666;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addWidget(title_container)
        layout.addStretch()

        btn_cancel = ModernButton("İptal")
        btn_cancel.setFixedWidth(130)
        btn_cancel.clicked.connect(self.close)
        
        btn_save = ModernButton("Asistan Oluştur", primary=True)
        btn_save.setFixedWidth(200)
        btn_save.clicked.connect(self.save_scenario)
        
        layout.addWidget(btn_cancel)
        layout.addSpacing(15)
        layout.addWidget(btn_save)
        return header

    def create_column_frame(self, title):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { 
                background: #050505; 
                width: 8px; 
                margin: 0px; 
                border-radius: 4px; 
            }
            QScrollBar::handle:vertical { 
                background: #333; 
                min-height: 30px; 
                border-radius: 4px; 
            }
            QScrollBar::handle:vertical:hover { background: #2769ff; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                height: 0px; 
                background: none; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
                background: none; 
            }
        """)
        
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label = QLabel(title)
        label.setFont(QFont("SF Pro Display", 13, QFont.Bold))
        label.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(label)
        
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #333;")
        layout.addWidget(sep)
        
        scroll.setWidget(frame)
        return scroll, layout

    def create_general_settings(self):
        scroll, layout = self.create_column_frame("SENARYO")
        
        layout.addWidget(SectionLabel("Senaryo"))
        self.scenario_input = ModernTextEdit("Senaryo açıklaması ve direktifleri...")
        self.scenario_input.setMinimumHeight(150)
        layout.addWidget(self.scenario_input)
        
        layout.addWidget(SectionLabel("Görev Tanımı"))
        self.desc_input = ModernTextEdit("Kısa açıklama...")
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)
        
        layout.addSpacing(20)
        
        layout.addWidget(SectionLabel("Hazır Senaryolar"))
        self.scenario_template_layout = QVBoxLayout()
        template_container = QWidget()
        template_container.setLayout(self.scenario_template_layout)
        self.refresh_scenario_template_list()
        layout.addWidget(template_container)
        
        save_btn = QPushButton("Senaryo Kaydet")
        save_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px dashed #444;
                border-radius: 8px;
                padding: 10px;
                color: #666;
            }
            QPushButton:hover {
                border: 1px dashed #3b82f6;
                color: #3b82f6;
            }
        """)
        save_btn.clicked.connect(self.save_current_as_template)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        return scroll

    def create_evaluation(self):
        scroll, layout = self.create_column_frame("DEĞERLENDİRME")
        
        layout.addWidget(SectionLabel("Değerlendirme Metrikleri"))
        self.evaluation_metrics_input = ModernTextEdit("Değerlendirme kriterleri ve metrikleri...")
        self.evaluation_metrics_input.setMinimumHeight(150)
        layout.addWidget(self.evaluation_metrics_input)
        
        layout.addSpacing(20)
        
        layout.addWidget(SectionLabel("Hazır Degerlendirme Metrikleri"))
        self.evaluation_template_layout = QVBoxLayout()
        template_container = QWidget()
        template_container.setLayout(self.evaluation_template_layout)
        self.refresh_evaluation_template_list()
        layout.addWidget(template_container)
        
        save_btn = QPushButton("Metrik Kaydet")
        save_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px dashed #444;
                border-radius: 8px;
                padding: 10px;
                color: #666;
            }
            QPushButton:hover {
                border: 1px dashed #3b82f6;
                color: #3b82f6;
            }
        """)
        save_btn.clicked.connect(self.save_current_as_evaluation_template)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        return scroll

    def on_voice_selected(self, selected_val):
        for val, card in self.voice_cards.items():
            card.set_selected(val == selected_val)

    def create_scenario_display(self):
        scroll, layout = self.create_column_frame("ASISTAN")
        
        layout.addWidget(SectionLabel("Asistan Adı"))
        self.scenario_name_input = ModernInput("Asistan Adı")
        layout.addWidget(self.scenario_name_input)
        
        layout.addSpacing(15)
        
        layout.addWidget(SectionLabel("Kullanıcı Rolü"))
        self.user_role_input = ModernInput("Ör: Acil Durum Operatörü")
        layout.addWidget(self.user_role_input)
        
        layout.addSpacing(15)
        
        layout.addWidget(SectionLabel("AI Rolü"))
        self.ai_role_input = ModernInput("Ör: Hasta (Arayan)")
        layout.addWidget(self.ai_role_input)
        
        layout.addSpacing(20)
        
        layout.addWidget(SectionLabel("Mini Asistan Fotoğrafı"))
        layout.addSpacing(8)
        
        photo_row = QHBoxLayout()
        photo_row.setSpacing(15)
        photo_row.setContentsMargins(0, 0, 0, 0)
        
        photo_row.addStretch()
        
        self.avatar_upload_label = QLabel()
        self.avatar_upload_label.setFixedSize(120, 120)
        self.avatar_upload_label.setStyleSheet("background: #0a0a0a; border: 2px dashed #333; border-radius: 8px;")
        self.avatar_upload_label.setAlignment(Qt.AlignCenter)
        self.avatar_upload_label.setText("Tıkla")
        self.avatar_upload_label.setCursor(Qt.PointingHandCursor)
        self.avatar_upload_label.mousePressEvent = lambda e: self.upload_scenario_photo()
        photo_row.addWidget(self.avatar_upload_label)
        
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(80, 80)
        plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #2769ff;
                color: white;
                font-size: 40px;
                border-radius: 40px;
                border: none;
                font-weight: 300;
            }
            QPushButton:hover { background-color: #3b7dff; }
            QPushButton:pressed { background-color: #1f5ccf; }
        """)
        plus_btn.setCursor(Qt.PointingHandCursor)
        plus_btn.clicked.connect(self.save_scenario)
        photo_row.addWidget(plus_btn)
        
        photo_row.addStretch()
        
        layout.addLayout(photo_row)
        layout.addStretch()
        return scroll

    def upload_scenario_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Asistan Fotoğrafı Seç", "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.gif);;Tüm Dosyalar (*)"
        )
        if file_path:
            self.default_avatar_path = file_path
            pixmap = QPixmap(file_path).scaledToWidth(120, Qt.SmoothTransformation)
            self.avatar_upload_label.setPixmap(pixmap)

    def refresh_scenario_template_list(self):
        while self.scenario_template_layout.count():
            child = self.scenario_template_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        for key, data in self.templates_data.items():
            if "evaluation_metrics" not in data:  # Senaryo templatelerini göster
                is_custom = key.startswith("custom_")
                self.scenario_template_layout.addWidget(TemplateItem(data["name"], is_custom, lambda c=False, d=data: self.apply_template_data(d), lambda c=False, k=key: self.delete_template(k)))
    
    def refresh_evaluation_template_list(self):
        while self.evaluation_template_layout.count():
            child = self.evaluation_template_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        for key, data in self.templates_data.items():
            if "evaluation_metrics" in data:  # Degerlendirme templatelerini göster
                is_custom = key.startswith("custom_eval_")
                self.evaluation_template_layout.addWidget(TemplateItem(data["name"], is_custom, lambda c=False, d=data: self.apply_evaluation_template_data(d), lambda c=False, k=key: self.delete_template(k)))
    
    def delete_template(self, k):
        del self.templates_data[k]
        self.save_templates_to_file()
        self.refresh_scenario_template_list()
        self.refresh_evaluation_template_list()
    
    def apply_template_data(self, d):
        if self.scenario_input:
            self.scenario_input.setPlainText(d.get("description", ""))
        if self.desc_input:
            self.desc_input.setPlainText(d.get("name", ""))
    
    def apply_evaluation_template_data(self, d):
        if self.evaluation_metrics_input:
            self.evaluation_metrics_input.setPlainText(d.get("evaluation_metrics", ""))
    
    def save_current_as_template(self):
        dialog = CustomInputDialog("Kaydet", "Senaryo Adı:", parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.input_text:
            self.templates_data["custom_"+dialog.input_text.lower().replace(" ","_")] = {"name":dialog.input_text, "description":self.scenario_input.toPlainText()}
            self.save_templates_to_file()
            self.refresh_scenario_template_list()
    
    def save_current_as_evaluation_template(self):
        dialog = CustomInputDialog("Metrik Kaydet", "Metrik Adı:", parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.input_text:
            self.templates_data["custom_eval_"+dialog.input_text.lower().replace(" ","_")] = {
                "name": dialog.input_text, 
                "evaluation_metrics": self.evaluation_metrics_input.toPlainText()
            }
            self.save_templates_to_file()
            self.refresh_evaluation_template_list()
    
    def save_templates_to_file(self):
        with open(self.templates_file, "w", encoding="utf-8") as f:
            json.dump(self.templates_data, f, indent=4, ensure_ascii=False)

    def save_scenario(self):
        scenario_name = self.scenario_name_input.text().strip() if self.scenario_name_input else ""
        scenario_content = self.scenario_input.toPlainText().strip() if self.scenario_input else ""
        description = self.desc_input.toPlainText().strip() if self.desc_input else ""
        evaluation_metrics = self.evaluation_metrics_input.toPlainText().strip() if self.evaluation_metrics_input else ""
        user_role = self.user_role_input.text().strip() if self.user_role_input else ""
        ai_role = self.ai_role_input.text().strip() if self.ai_role_input else ""
        
        if not scenario_name:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen asistana bir isim verin!")
            return
        
        if not scenario_content:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen senaryo açıklaması yazın!")
            return
        
        scenario_id = str(uuid.uuid4())
        scenario_data = {
            "id": scenario_id,
            "name": scenario_name,
            "description": description,
            "scenario": scenario_content,
            "user_role": user_role,
            "ai_role": ai_role,
            "evaluation_metrics": evaluation_metrics,
            "avatar": self.default_avatar_path,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            filename = f"{scenario_id}.json"
            with open(os.path.join(self.scenarios_path, filename), "w", encoding="utf-8") as f:
                json.dump(scenario_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Başarılı", f"Asistan '{scenario_name}' kaydedildi!")
            
            from ui.scenario_selector import ScenarioSelector
            self.selector = ScenarioSelector()
            self.selector.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt başarısız: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScenarioCreatorUI()
    window.show()
    sys.exit(app.exec_())