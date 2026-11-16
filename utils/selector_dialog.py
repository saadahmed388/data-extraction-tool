from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
)

class SelectorDialog(QDialog):
    def __init__(self, title, label_text, items_list, parent=None):
        super().__init__(parent)
    
        self.setWindowTitle(title)
        self.resize(400, 170)  
        
        layout = QVBoxLayout()
        layout.setSpacing(15)  
         
        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.label)
            
        self.combobox = QComboBox()
        self.combobox.addItems(items_list)
        self.combobox.setStyleSheet("""
            QComboBox { 
                padding: 6px; 
                font-size: 14px; 
                min-height: 25px; 
            }
        """)
        
        layout.addWidget(self.combobox)
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.setStyleSheet("QPushButton { min-width: 80px; padding: 5px; }")
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        
    def get_selected_item(self):        
        return self.combobox.currentText()
        
    