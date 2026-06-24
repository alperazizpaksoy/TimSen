import sys
import requests # API isteği için gerekli
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QFrame, QScrollArea, QCheckBox, QRadioButton,
    QButtonGroup, QSizePolicy, QGridLayout, QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QThread, QRect, QPoint
from PyQt5.QtGui import QFont, QCursor, QColor, QPainter, QPen, QBrush, QFontMetrics, QPainterPath
from config import HF_API_KEY

# ---------------------------------------------------------
# 1. SEARCH WORKER (DÜZELTİLDİ: DIRECT REQUEST)
# ---------------------------------------------------------
class SearchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, api_key, query, filters=None):
        super().__init__()
        self.api_key = api_key
        self.query = query
        self.filters = filters if filters else {}

    def run(self):
        try:
            url = "https://huggingface.co/api/models"
            
            params = {
                "search": self.query,
                "limit": 50,
                "sort": self.filters.get("sort", "likes"),
                "direction": "-1"
            }
            
            # Format seçimlerine göre arama yap (seçim yoksa tüm modelleri ara)
            format_filters = self.filters.get("format", [])
            
            # Eğer format seçilmişse filtrele
            if format_filters and len(format_filters) > 0:
                params["filter"] = format_filters[0]

            # Task filtresi varsa ekle
            if "task" in self.filters and self.filters["task"]:
                params["pipeline_tag"] = self.filters["task"][0]

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.finished.emit(data)
            else:
                self.error.emit(f"API Hatası: {response.status_code}")
                
        except Exception as e:
            self.error.emit(str(e))

# ---------------------------------------------------------
# 2. TECH CHECKBOX (TASARIM AYNI)
# ---------------------------------------------------------
class TechCheckBox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QCheckBox {
                color: #888888;
                font-size: 13px;
                font-family: 'Segoe UI';
                spacing: 10px;
                background: transparent;
            }
            QCheckBox:hover {
                color: white;
            }
            QCheckBox::indicator { width: 16px; height: 16px; background: transparent; }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Kutuyu Çiz
        box_rect = QRect(0, 2, 16, 16)
        
        pen = QPen(QColor("#444444"))
        pen.setWidth(1)
        
        if self.isChecked():
            pen.setColor(QColor("#3b82f6"))
            pen.setWidth(2)
        elif self.underMouse():
            pen.setColor(QColor("#666666"))
            
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(box_rect, 4, 4)

        # Tik İşaretini Çiz
        if self.isChecked():
            path = QPainterPath()
            path.moveTo(4, 9)
            path.lineTo(7, 12)
            path.lineTo(12, 5)
            
            check_pen = QPen(QColor("#3b82f6"))
            check_pen.setWidth(2)
            check_pen.setCapStyle(Qt.RoundCap)
            check_pen.setJoinStyle(Qt.RoundJoin)
            
            painter.setPen(check_pen)
            painter.drawPath(path)

        # Metni Çiz
        painter.setPen(QColor("#cccccc") if not self.underMouse() else QColor("#ffffff"))
        font = self.font()
        painter.setFont(font)
        text_rect = self.rect()
        text_rect.setLeft(24)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())


# ---------------------------------------------------------
# 3. TECH ICON (Büyüteç - Dolgusuz Neon) (TASARIM AYNI)
# ---------------------------------------------------------
class TechIcon(QPushButton):
    def __init__(self, icon_type="search", size=24):
        super().__init__()
        self.setFixedSize(size + 10, size + 10)
        self.icon_type = icon_type
        self.is_hovered = False
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.is_hovered:
            pen_color = QColor("#82b1ff")
            line_width = 2.5
        else:
            pen_color = QColor("#3b82f6")
            line_width = 2.0

        pen = QPen(pen_color)
        pen.setWidthF(line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        if self.icon_type == "search":
            radius = 8
            painter.drawEllipse(QPoint(int(cx - 2), int(cy - 2)), radius, radius)
            offset = radius * 0.7
            painter.drawLine(int(cx - 2 + offset), int(cy - 2 + offset), int(cx + 8), int(cy + 8))

# ---------------------------------------------------------
# 4. ELIDED LABEL (TASARIM AYNI)
# ---------------------------------------------------------
class ElidedLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.setToolTip(text)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.full_text, Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

# ---------------------------------------------------------
# 5. MODEL KARTI (TASARIM AYNI)
# ---------------------------------------------------------
class ModelCard(QFrame):
    selectClicked = pyqtSignal(str) 

    def __init__(self, model_data):
        super().__init__()
        self.model_id = model_data.get("modelId") or model_data.get("id", "Unknown")
        self.likes = model_data.get("likes", 0)
        self.downloads = model_data.get("downloads", 0)
        
        if "/" in self.model_id:
            self.author, self.model_name = self.model_id.split("/", 1)
        else:
            self.author = "HuggingFace"
            self.model_name = self.model_id

        self.setFixedHeight(100)
        self.setStyleSheet("""
            QFrame {
                background-color: #151922;
                border: 1px solid #2b3242;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1px solid #2769ff;
                background-color: #1a1e29;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_lbl = ElidedLabel(self.model_name)
        name_lbl.setStyleSheet("color: white; font-size: 15px; font-weight: bold; border: none; background: transparent;")
        info_layout.addWidget(name_lbl)

        author_lbl = QLabel(f"@{self.author}")
        author_lbl.setStyleSheet("color: #3b82f6; font-size: 11px; border: none; background: transparent;")
        info_layout.addWidget(author_lbl)

        meta_text = f"★ {self.likes}  •  ⬇ {self.downloads}"
        meta_lbl = QLabel(meta_text)
        meta_lbl.setStyleSheet("color: #5d6675; font-size: 11px; font-weight: 500; border: none; background: transparent;")
        info_layout.addWidget(meta_lbl)

        layout.addLayout(info_layout, stretch=1)

        self.select_btn = QPushButton("Seç")
        self.select_btn.setFixedSize(80, 32)
        self.select_btn.setCursor(Qt.PointingHandCursor)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #333b4d;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2769ff;
                border-color: #2769ff;
            }
        """)
        self.select_btn.clicked.connect(self.emit_selection)
        layout.addWidget(self.select_btn)

    def emit_selection(self):
        self.selectClicked.emit(self.model_id)

# ---------------------------------------------------------
# 6. FİLTRE PANELİ (TASARIM AYNI)
# ---------------------------------------------------------
class FilterPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QWidget { background: transparent; }
            QLabel { 
                color: #888888; 
                font-size: 11px; 
                font-weight: bold; 
                margin-top: 15px; 
                margin-bottom: 8px; 
                font-family: 'Segoe UI';
            }
            QRadioButton { 
                color: #cccccc; 
                spacing: 8px; 
                font-size: 13px;
                margin-bottom: 6px; 
            }
            QRadioButton::indicator { 
                width: 14px; 
                height: 14px; 
                border-radius: 7px; 
                border: 1px solid #555; 
                background: transparent; 
            }
            QRadioButton::indicator:checked { 
                background-color: #3b82f6; 
                border: 2px solid #0B0D13; 
                outline: 1px solid #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 15, 0) 
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("TASK TÜRÜ"))
        self.chk_text = TechCheckBox("Text Generation")
        self.chk_vision = TechCheckBox("Vision / Image")
        self.chk_audio = TechCheckBox("Audio")
        layout.addWidget(self.chk_text)
        layout.addWidget(self.chk_vision)
        layout.addWidget(self.chk_audio)

        layout.addWidget(QLabel("BOYUT"))
        self.chk_small = TechCheckBox("Small (< 7B)")
        self.chk_medium = TechCheckBox("Medium (7B - 13B)")
        self.chk_large = TechCheckBox("Large (30B+)")
        layout.addWidget(self.chk_small)
        layout.addWidget(self.chk_medium)
        layout.addWidget(self.chk_large)

        layout.addWidget(QLabel("FORMAT"))
        self.chk_gguf = TechCheckBox("GGUF (llama-cpp)")
        self.chk_transformers = TechCheckBox("Transformers (.bin)")
        self.chk_safetensors = TechCheckBox("SafeTensors")
        layout.addWidget(self.chk_gguf)
        layout.addWidget(self.chk_transformers)
        layout.addWidget(self.chk_safetensors)

        layout.addWidget(QLabel("SIRALAMA"))
        self.sort_group = QButtonGroup(self)
        
        rb1 = QRadioButton("En Popüler (Likes)")
        rb1.setChecked(True)
        layout.addWidget(rb1)
        self.sort_group.addButton(rb1, 1)
        
        rb2 = QRadioButton("En Yeni")
        layout.addWidget(rb2)
        self.sort_group.addButton(rb2, 2)

        rb3 = QRadioButton("İndirilme Sayısı")
        layout.addWidget(rb3)
        self.sort_group.addButton(rb3, 3)

        layout.addStretch()

    def get_filters(self):
        filters = {
            "task": [],
            "size": [],
            "sort": "likes",
            "format": []
        }
        if self.chk_text.isChecked(): filters["task"].append("text-generation")
        if self.chk_vision.isChecked(): filters["task"].append("image-classification")
        
        # Format seçimleri
        if self.chk_gguf.isChecked(): filters["format"].append("gguf")
        if self.chk_transformers.isChecked(): filters["format"].append("bin")
        if self.chk_safetensors.isChecked(): filters["format"].append("safetensors")
        
        checked_id = self.sort_group.checkedId()
        if checked_id == 2: filters["sort"] = "lastModified"
        elif checked_id == 3: filters["sort"] = "downloads"
        
        return filters

# ---------------------------------------------------------
# 7. ANA PENCERE (TASARIM AYNI)
# ---------------------------------------------------------
class ModelSelector(QWidget):
    modelSelected = pyqtSignal(str)

    def __init__(self, parent=None, part_name=None):
        super().__init__(parent)
        self.part_name = part_name
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1000, 720)
        
        self.main_container = QFrame(self)
        self.main_container.setStyleSheet("""
            QFrame#MainContainer {
                background-color: #0B0D13;
                border: 1px solid #333b4d; 
                border-radius: 12px;
            }
            QLabel { font-family: 'Segoe UI', sans-serif; }
            QScrollBar:vertical {
                border: none;
                background: #0B0D13;
                width: 6px;
                margin: 0px; 
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 30px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover { background: #3b82f6; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        self.main_container.setObjectName("MainContainer")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_container)

        self.inner_layout = QVBoxLayout(self.main_container)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)

        self.create_title_bar()
        
        content_wrapper = QHBoxLayout()
        content_wrapper.setContentsMargins(25, 25, 25, 25)
        content_wrapper.setSpacing(0)
        
        self.filter_panel = FilterPanel()
        content_wrapper.addWidget(self.filter_panel)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # -- Arama Barı --
        search_container = QHBoxLayout()
        search_container.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Model ara (örn: llama3, mistral)")
        self.search_input.setFixedHeight(42)
        # NEON GLOW Efekti
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #151922;
                border: 2px solid #2b3242; 
                border-radius: 21px; 
                padding-left: 20px;
                padding-right: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:hover {
                border-color: #4a5568; 
            }
            QLineEdit:focus { 
                border-color: #3b82f6; 
                background-color: #1a1e29;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.search_input.setGraphicsEffect(shadow)
        
        self.search_input.returnPressed.connect(self.start_search)
        
        self.search_btn = TechIcon(icon_type="search", size=32)
        self.search_btn.clicked.connect(self.start_search)

        search_container.addWidget(self.search_input)
        search_container.addWidget(self.search_btn)
        right_panel.addLayout(search_container)

        # -- Scroll Area --
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.scroll_content)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(0, 0, 5, 0)
        self.cards_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        right_panel.addWidget(self.scroll_area)
        
        self.status_label = QLabel("Popüler modeller için arama yapın...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; margin-top: 5px;")
        right_panel.addWidget(self.status_label)

        content_wrapper.addLayout(right_panel, stretch=1)
        self.inner_layout.addLayout(content_wrapper)

    def create_title_bar(self):
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #0F131A;
                border-bottom: 1px solid #1f1f1f;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        layout = QHBoxLayout(self.title_bar)
        layout.setContentsMargins(20, 0, 10, 0)

        header_text = f"{self.part_name} Seçimi" if self.part_name else "Model Store"
        lbl = QLabel(header_text)
        lbl.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none; letter-spacing: 0.5px;")
        layout.addWidget(lbl)
        
        layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: #666; border: none; font-weight: bold; } QPushButton:hover { color: #ff3b30; }")
        layout.addWidget(close_btn)
        
        self.inner_layout.addWidget(self.title_bar)
        self.title_bar.mousePressEvent = self.mousePressEvent
        self.title_bar.mouseMoveEvent = self.mouseMoveEvent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + (event.globalPos() - self.dragPos))
            self.dragPos = event.globalPos()

    def start_search(self):
        query = self.search_input.text().strip()
        if not query:
            self.status_label.setText("Lütfen bir model adı girin.")
            return

        self.status_label.setText("Aranıyor...")
        self.search_btn.setEnabled(False) 

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        filters = self.filter_panel.get_filters()
        self.worker = SearchWorker(HF_API_KEY, query, filters)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()

    def on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        if not results:
            self.status_label.setText("Model bulunamadı. Farklı arama terimi deneyin.")
            return

        for model in results:
            model_data = {
                "id": model.get("modelId") or model.get("id"),
                "likes": model.get("likes", 0),
                "downloads": model.get("downloads", 0)
            }
            card = ModelCard(model_data)
            card.selectClicked.connect(self.on_model_selected)
            self.cards_layout.addWidget(card)
        
        self.status_label.setText(f"{len(results)} model bulundu.")

    def on_search_error(self, error_msg):
        self.search_btn.setEnabled(True)
        self.status_label.setText("Bağlantı hatası oluştu.")
        print(f"Search Error: {error_msg}")

    def on_model_selected(self, model_id):
        self.modelSelected.emit(model_id)
        self.close()