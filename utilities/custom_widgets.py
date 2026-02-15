from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QTextEdit
from utilities.stylesheets import StylingManager

class StyledInputDialog(QDialog):
    def __init__(self, title, label, caps = "N", default_text = "", num_lines = "S"):
        super().__init__()
        self.styling_manager = StylingManager()
        self.setWindowTitle(title)
        self.resize(400, 150)
        self.setStyleSheet(self.styling_manager.dialog_style())   
        self.caps = caps

        layout = QVBoxLayout(self)
        self.label = QLabel(label)

        
        if num_lines == "M":
            self.input = QTextEdit()
            self.resize(600, 300)
        elif num_lines == "S":
            self.input = QLineEdit()
        else:
            QMessageBox.warning(self, "Invalid Argment", "Please provide valid Text Box size argument. M for Multi-line, S for Single-line")
            return
                
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
        self.result = self.exec_()
        if isinstance(self.input, QLineEdit):
            text = self.input.text().strip()
        elif isinstance(self.input, QTextEdit):
            text = self.input.toPlainText().strip()
        else:
            text = ""
        if self.caps.upper() == "Y":
            text = text.upper()
        return text, self.result == QDialog.Accepted

