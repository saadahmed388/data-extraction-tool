from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QTableWidget, QTableWidgetItem, QDialog, QStyle
)

from utils.log_viewer import LogViewer
from typing import TYPE_CHECKING

import logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.managers.history_manager import HistoryManager

class HistoryTab(QWidget):
    
    def __init__(self, history_manager: HistoryManager, styling_manager):
    
        super().__init__()      
        
        self.styling_manager = styling_manager
        self.history_manager = history_manager
        
        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['SR#', 'Config', 'Date Extracted', 'Extraction Log', 'Runtime'])
        self.tree.setColumnWidth(2, 200)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        self.tree.setIndentation(0)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.history = []        
        self.load_history()
        self.history_manager.history_updated.connect(self.load_history)
        
    def load_history(self):

        try:

            self.tree.clear()
            self.history = self.history_manager.all_history
            
            for history_id, history_details in self.history.items():                
                sr_num = history_details.get("sr_num", "")
                config_name = history_details.get("config", "")
                date_extracted = history_details.get("date_extracted", "")
                extraction_log = history_details.get("extraction_log", "")
                runtime_duration = history_details.get("runtime_duration", 0)
                
                item = QTreeWidgetItem([sr_num, config_name, date_extracted, '', runtime_duration])
                self.tree.addTopLevelItem(item)
                
                # 🔍 Preview button
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                preview_btn.clicked.connect(lambda _, s = self.styling_manager, e = extraction_log, l = LogViewer : self.show_log(s, e, l))
                self.tree.setItemWidget(item, 3, preview_btn)

        except Exception as e:
                
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
                               
    
    def show_table(self, sr_num, config, extraction_log):

        try:

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

        except Exception as e:
                
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def show_log(self, styling_manager, extraction_log, LogViewer):

        try:
            
            self.log_viewer = LogViewer(styling_manager, extraction_log)
            self.log_viewer.exec_()

        except Exception as e:
                
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
        
        