# ==================== Data Extraction App ====================
# ---------------- app.py ----------------
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt5.QtGui import QIcon


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/data_extcn_app_icon.png"))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())