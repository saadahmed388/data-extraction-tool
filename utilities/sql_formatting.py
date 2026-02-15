from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, QRegExp
import sys


class SqlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SqlHighlighter, self).__init__(parent)

        # --- Define text formats ---
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0077cc"))
        keyword_format.setFontWeight(QFont.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#d14"))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#098658"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#888888"))
        comment_format.setFontItalic(True)

        # --- Regex rules ---
        self.rules = []

        keywords = [
            "SELECT", "FROM", "WHERE", "AND", "OR", "INSERT", "UPDATE", "DELETE",
            "CREATE", "ALTER", "DROP", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
            "GROUP", "BY", "ORDER", "HAVING", "AS", "ON", "INTO", "VALUES", "NOT", "NULL"
        ]

        for kw in keywords:
            pattern = QRegExp(rf"\b{kw}\b")
            pattern.setCaseSensitivity(Qt.CaseInsensitive)
            self.rules.append((pattern, keyword_format))

        # Strings
        self.rules.append((QRegExp("'[^']*'"), string_format))

        # Numbers
        self.rules.append((QRegExp(r"\b[0-9]+\b"), number_format))

        # Comments (single-line)
        self.rules.append((QRegExp(r"--[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            i = pattern.indexIn(text)
            while i >= 0:
                length = pattern.matchedLength()
                self.setFormat(i, length, fmt)
                i = pattern.indexIn(text, i + length)


class SqlPreview(QMainWindow):
    def __init__(self, sql_text):
        super().__init__()
        self.setWindowTitle("SQL Preview")
        self.resize(1200, 800)

        editor = QPlainTextEdit()
        editor.setStyleSheet("QPlainTextEdit { background-color: #f9f9f9; color: #222; }")
        editor.setPlainText(sql_text)
        editor.setReadOnly(True)
        editor.setFont(QFont("Consolas", 11))

        # ✅ Attach syntax highlighter AFTER setting text
        self.highlighter = SqlHighlighter(editor.document())

        self.setCentralWidget(editor)
