from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.stylesheets import StylingManager

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox
)

class PermissionDialog(QDialog):
    def __init__(self, 
            message_str: str, 
            styling_manager: StylingManager
        ):
        super().__init__()
        
        self.resize(300, 100)
        self.styling_manager = styling_manager
        self.setStyleSheet(self.styling_manager.dialog_style())
        self.setWindowTitle("Permission Dialog")

        layout = QVBoxLayout()
        
        label = QLabel(message_str + '\nPress OK to proceed...', self)
        layout.addWidget(label)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        self.setLayout(layout)
            