from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QListView
)
from PyQt5.QtCore import Qt
from utils.stylesheets import StylingManager

class SelectorDialog(QDialog):
    def __init__(self, title, label_text, items_list, parent=None):
        super().__init__(parent)

        self.styling_manager = StylingManager()
        self.setWindowTitle(title)
        self.resize(400, 170)  
        self.setStyleSheet(self.styling_manager.dialog_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(15)  
         
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
            
        self.combobox = QComboBox()
        self.combobox.setView(QListView())                
        self.combobox.setObjectName("selector")
        self.combobox.setAttribute(Qt.WA_StyledBackground, True)
        self.combobox.setStyleSheet(self.styling_manager.selector_box_style("selector"))
        self.combobox.view().setStyleSheet(self.styling_manager.selector_style())
        self.combobox.addItems(items_list)
        
        layout.addWidget(self.combobox)
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        
    def get_selected_item(self):        
        return self.combobox.currentText()
        
    