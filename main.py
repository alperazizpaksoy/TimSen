import os
import sys

# --- KRİTİK DÜZELTME: TENSORFLOW / PYTORCH ÇAKIŞMASINI ENGELLEME ---
# Bu kodlar, "DLL load failed" hatasını çözer ve Transformers kütüphanesini
# TensorFlow yerine PyTorch kullanmaya zorlar.
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["USE_TORCH"] = "1"
os.environ["USE_TF"] = "0"
# -------------------------------------------------------------------

from PyQt5.QtWidgets import QApplication
from ui.overlay import TimurOverlay

def main():
    app = QApplication(sys.argv)
    
    # Uygulama stilini ayarla
    app.setStyle('Fusion')
    
    # Overlay sürekli açık kalacağı için son pencere kapansa da uygulama kapanmasın
    app.setQuitOnLastWindowClosed(False)
    
    # --- BAŞLANGIÇ NOKTASI: OVERLAY ---
    overlay = TimurOverlay()
    overlay.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()