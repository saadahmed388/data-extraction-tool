# ==================== Data Extraction App ====================
# ---------------- app.py ----------------
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt5.QtGui import QIcon
from utilities.logger_config import setup_logging
from utilities.ss import elegant_qss
import logging

setup_logging()

logger = logging.getLogger(__name__)
logger.info("Application Started")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon("assets/data_extcn_app_icon.png"))
        
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())
    except Exception:
        logger.exception("Unhandled Exception")