class StylingManager:
    def button_style(self):
        return """
            QPushButton {
                background-color: #fafafa;
                color: #555;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 22px;          /* Increased top-bottom padding */
                font-size: 7pt;             /* Slightly larger for elegance */
                font-weight: 500;
                letter-spacing: 1.2px;
                min-height: 42px;           /* Slightly taller */
                min-width: 130px;
                outline: none;
            }
            

            QPushButton:hover {
                background-color: #1bc29f;
                color: #fff;
                border: 1px solid #c5c5c5;
            }

            QPushButton:pressed {
                background-color: #e6e6e6;
                border: 1px solid #b8b8b8;
            }

            QPushButton:focus {
                border: 1px solid #a6a6a6;
            }

            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
                border: 1px solid #e0e0e0;
            }
            """


    def header_style(self):
        return """
            QHeaderView::section {
                background: #fafafa;
                color: #333;
                font-size: 9pt;
                font-weight: 500;
                border-top: none;
                border-bottom: 1px solid #dcdcdc;
                border-right: 1px solid #e6e6e6;  /* subtle column separator */
                padding: 6px 10px;
                text-align: center;
            }

            QTreeWidget {
                background: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                font-size: 8pt;
                color: #444;
                selection-background-color: #e6f0ff;
                selection-color: #000;
                alternate-background-color: #fafafa;
            }

            QTreeWidget::item {
                padding: 4px 4px;
                border: none;
                height: 40px;
            }

            QTreeWidget::item:selected {
                background-color: #e6f0ff;
                color: #000;
            }

            QTreeWidget::item:hover {
                background-color: #1bc29f;
            }

            QHeaderView {
                border-bottom: 1px solid #dcdcdc;
            }
        """
    def tab_style(self):
        return """
            QTabWidget::pane {
                border: 1px solid #dcdcdc;
                border-radius: 3px;
                background: #fafafa;
                padding: 4px; /* Prevent cut-off when tab selected */
            }

            QTabBar::tab {
                border: none;
                background: transparent;
                padding: 10px 16px;  /* Increased padding for larger clickable area */
                margin-right: 6px;
                color: #444;
                font-size: 7.5pt;  /* Slightly larger font */
                min-width: 160px;    /* Ensures consistent tab width */
                min-height: 30px;    /* taller tabs */
            }

            QTabBar::tab:selected {
                border-bottom: 3px solid #0078d7;
                color: #000;
                font-weight: 600;
                background: #ffffff;
                border-top-left-radius: 2px;
                border-top-right-radius: 2px;
            }

            QTabBar::tab:hover {
                background: #1bc29f;
                color: #000;
            }
        """
    def button_bar_style(self):
        return """
            QWidget {
                background: #fdfdfd;
                border-bottom: 1px solid #e0e0e0;
                padding: 6px 10px;
            }
        """
    
    def dialog_style(self):
        return """
            QDialog {
                background-color: #fdfdfc;
                border: 1px solid #e4e4e4;
                border-radius: 12px;
                padding: 20px;
            }

            QLabel {
                color: #444;
                font-family: 'Segoe UI', 'Noto Sans', 'Open Sans';
                font-size: 10pt;
                letter-spacing: 0.4px;
                padding-bottom: 6px;
            }

            QLineEdit {
                background-color: #fcfcfb;
                border: 1px solid #d8d8d8;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
                font-family: 'Segoe UI', 'Open Sans';
                color: #333;
                selection-background-color: #c8def8;
                selection-color: #000;
            }

            QLineEdit:focus {
                border: 1px solid #b8b8b8;
                background-color: #ffffff;
            }

            QPushButton {
                background-color: #f7f7f7;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                color: #444;
                font-size: 9pt;
                font-family: 'Segoe UI Semibold';
                padding: 6px 18px;
                min-width: 90px;
            }

            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #c8c8c8;
            }

            QPushButton:pressed {
                background-color: #e8e8e8;
                border-color: #bcbcbc;
            }

            QPushButton#okButton {
                background-color: #ededed;
                border: 1px solid #c9c9c9;
                color: #2e2e2e;
            }

            QPushButton#okButton:hover {
                background-color: #e4e4e4;
                border-color: #bcbcbc;
            }

            QPushButton#cancelButton {
                background-color: #fafafa;
                border: 1px solid #dcdcdc;
                color: #555;
            }

            QPushButton#cancelButton:hover {
                background-color: #f2f2f2;
                border-color: #cfcfcf;
            }
        """
        
    def list_style(self):
        return """
            QListWidget {
                background-color: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 4px;
                font-size: 9pt;
            }
            QListWidget::item {
                padding: 8px 6px;
                margin: 3px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e5e5e5;
                color: #000;
                font-weight: 500;
            }
        """
        
    def selector_style(self):
        return  """
            QComboBox {
                font-size: 9pt;      /* Increase font */
                min-height: 30px;     /* Increase box height */
                padding: 4px;   /* Helps maintain shape */
                color: #555;
            }

            QComboBox QAbstractItemView {
                font-size: 7.5pt; 
                color: #555;
                selection-background-color: #e6f0ff;
                selection-color: #000;
                alternate-background-color: #fafafa;                /* Ensure dropdown list matches */
            }
            
            QComboBox QAbstractItemView::item {
                min-height: 40px;     /* height of dropdown rows */
                padding: 4px 6px;
            }
        """
    def selector_box_style(self, object_name):
        return f"""
                QComboBox#{object_name}"""+""" {
                font-size: 7pt;    
                min-height: 30px;  
                padding: 4px;   
                color: #555;
            }"""

        