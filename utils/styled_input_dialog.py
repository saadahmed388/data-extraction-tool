from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QPlainTextEdit,
)
from PyQt5.QtGui import QFont

from utils.stylesheets import StylingManager

class SingleLineInputDialog(QDialog):
    def __init__(self, title, label, caps = "N", default_text = ""):

        super().__init__()
        self.styling_manager = StylingManager()
        self.setWindowTitle(title)
        self.resize(400, 150)
        self.setStyleSheet(self.styling_manager.dialog_style())   
        self.caps = caps

        layout = QVBoxLayout(self)
        self.label = QLabel(label)
        
        self.input = QLineEdit()
        self.input.setText(default_text)
        self.input.setPlaceholderText("Type here...")
        layout.addWidget(self.label)
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_text(self):

        result = self.exec_()
        text = self.input.text().strip()
        if self.caps.upper() == "Y":
            text = text.upper()
        return text, result == QDialog.Accepted


class MultiLineInputDialog(QDialog):
    def __init__(self, title, label, default_text = ""):

        super().__init__()
        self.styling_manager = StylingManager()
        self.setWindowTitle(title)
        self.resize(800, 400)
        self.setStyleSheet(self.styling_manager.dialog_style())   

        layout = QVBoxLayout(self)
        self.label = QLabel(label)
        
        self.input = QPlainTextEdit()
        self.input.setPlainText(default_text)
        self.input.setPlaceholderText("Type here...")
        self.input.setFont(QFont("Consolas", 11))
        layout.addWidget(self.label)
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_text(self):

        result = self.exec_()
        text = self.input.toPlainText().strip()
        return text, result == QDialog.Accepted

