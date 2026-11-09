# A modern, elegant dark-slate minimal theme
elegant_qss = """
    /* Main Window & Dialog background */
    QDialog, QMainWindow, QWidget {
        background-color: #1e1e24;
        color: #e2e8f0;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Labels - Clean typography hierarchy */
    QLabel {
        font-size: 13px;
        color: #94a3b8; /* Soft slate gray so text isn't aggressively bright */
    }
    
    /* Input Elements & Dropdowns */
    QComboBox {
        background-color: #2d2d34;
        border: 1px solid #3f3f46;
        border-radius: 6px;
        padding: 6px 12px;
        color: #f8fafc;
        font-size: 13px;
    }
    QComboBox:hover {
        border-color: #6366f1; /* Indigo accent highlight on hover */
    }

    /* Modern Flat Buttons */
    QPushButton {
        background-color: #312e81; /* Deep rich indigo */
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #4338ca;
    }
    QPushButton:pressed {
        background-color: #3730a3;
    }
"""
