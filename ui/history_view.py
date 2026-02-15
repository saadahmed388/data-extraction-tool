from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
import json
import os
import uuid
from utilities.utils import LogViewer

class HistoryTab(QWidget):
    def __init__(self, styling_manager, history_manager):
        super().__init__()      
        
        self.styling_manager = styling_manager
        self.history_manager = history_manager
        
        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['SR#', 'Preset', 'Date Extracted', 'Extraction Log'])
        self.tree.setColumnWidth(2, 200)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        self.tree.setIndentation(0)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.history = []        
        self.load_history()
        self.history_manager.history_updated.connect(self.load_history)
        
    def load_history(self):
        
        self.tree.clear()
        self.history = self.history_manager.get_all_history()
        
        if self.history:
            for hist in self.history:                
                sr_num = hist.get("sr_num", "")
                config = hist.get("config", "")
                date_extracted = hist.get("date_extracted", "")
                extraction_log = hist.get("extraction_log", "")
                
                item = QTreeWidgetItem([sr_num, config, date_extracted, ''])
                self.tree.addTopLevelItem(item)
                
                # 🔍 Preview button
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                preview_btn.clicked.connect(lambda _, s = self.styling_manager, e = extraction_log, l = LogViewer : self.show_log(s, e, l))
                self.tree.setItemWidget(item, 3, preview_btn) 
                               
    
    def show_table(self, sr_num, config, extraction_log):

        rows = extraction_log
        
        if not rows:
            QMessageBox.information(self, "No Data", "No rows available for this extraction.")
            return        

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{config} - {sr_num}")
        dialog.resize(800, 400)

        layout = QVBoxLayout(dialog)

        table = QTableWidget(len(rows), len(rows[0]))
        table.setHorizontalHeaderLabels(list(rows[0].keys()))
        table.setStyleSheet(self.styling_manager.header_style())

        for i, row in enumerate(rows):
            for j, col in enumerate(row.keys()):
                table.setItem(i, j, QTableWidgetItem(str(row[col])))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet(self.styling_manager.button_style())
        layout.addWidget(close_btn)

        dialog.exec_()
            
    def show_log(self, styling_manager, extraction_log, LogViewer):
        self.log_viewer = LogViewer(styling_manager, extraction_log)
        self.log_viewer.exec_()
        
        