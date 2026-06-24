import time
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from config import ICON_PATH, WINDOW_WIDTH, WINDOW_HEIGHT, ICON_ICO


class TimurOverlay(QWidget):
    def __init__(self):
        super().__init__()

        try:
            # Resmi oku ve ölçeklendir
            self.original_pixmap = QPixmap(ICON_PATH).scaled(
                WINDOW_WIDTH, WINDOW_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            self.setWindowTitle("Timur Assistant")
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setFixedSize(self.original_pixmap.size())
            self.setWindowIcon(QIcon(ICON_ICO))

            # Ekranın sağ altına taşı
            screen = self.screen().geometry()
            self.move(
                screen.width() - self.original_pixmap.width(),
                screen.height() - self.original_pixmap.height() - 50
            )

            # İkon label
            self.label = QLabel(self)
            self.label.setGeometry(0, 0, self.original_pixmap.width(), self.original_pixmap.height())
            self.label.setPixmap(self.original_pixmap)

            # PNG maskesi (şeffafsa güzel görünür)
            try:
                self.setMask(self.original_pixmap.mask())
            except:
                pass

            # Mouse event
            self.label.mousePressEvent = self.handle_mouse_press
        except Exception as e:
            print(f"Overlay Hatası: {e}")
            # Hata olsa da overlay gösterilir
            self.setWindowTitle("Timur Assistant")
            self.setFixedSize(200, 200)


    def handle_mouse_press(self, event):
        if event.button() == Qt.RightButton:
            QApplication.quit()
            return

        if event.button() == Qt.LeftButton:
            self.open_assistant_selector()


    def open_assistant_selector(self):
        from ui.scenario_selector import ScenarioSelector
        self.selector = ScenarioSelector()
        self.selector.show()
