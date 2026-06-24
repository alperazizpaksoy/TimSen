"""
Tema rengine uygun custom mesaj kutuları
"""

from PyQt5.QtWidgets import QMessageBox, QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import QTimer


class ThemedMessageBox(QMessageBox):
    """Tema rengine uygun mesaj kutusu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QMessageBox {
                background-color: #0B0D13;
                border: 1px solid #2769ff;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 13px;
                font-family: 'SF Pro Display', 'Segoe UI';
            }
            QPushButton {
                background-color: #2769ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3b7dff;
            }
            QPushButton:pressed {
                background-color: #1f5ccf;
            }
        """)


def show_warning(parent, title, message):
    """Uyarı mesajı göster"""
    msg = ThemedMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Warning)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def show_info(parent, title, message):
    """Bilgi mesajı göster"""
    msg = ThemedMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def show_error(parent, title, message):
    """Hata mesajı göster"""
    msg = ThemedMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Critical)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def show_question(parent, title, message):
    """Soru mesajı göster (Yes/No)"""
    msg = ThemedMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Question)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = msg.exec_()
    return result == QMessageBox.Yes
