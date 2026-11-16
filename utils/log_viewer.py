from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton,
    QTreeWidget, QMessageBox, QTreeWidgetItem,
    QStyle
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.stylesheets import StylingManager
    from core.managers.history_manager import HistoryManager

class LogViewer(QDialog):
    def __init__(self, 
        styling_manager: StylingManager, 
        export_log = None
    ):
        super().__init__()

        self.setWindowTitle("Log Viewer")
        self.resize(600,300)

        self.styling_manager = styling_manager
        
        layout = QVBoxLayout()
        
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setIndentation(0)
        self.tree.setHeaderLabels(["Query", "Environment", "Record Count"])
        self.tree.setColumnWidth(0, 180)
        self.tree.setColumnWidth(1, 150)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        
        if export_log:
            for log in export_log:
                item = QTreeWidgetItem([str(log["sql_name"]), str(log["env"]), str(log["record_count"])])
                self.tree.addTopLevelItem(item)
                
        self.tree.expandAll()
        layout.addWidget(self.tree)
        self.setLayout(layout)

class TreePopUp(QDialog):
    def __init__(self, 
        styling_manager: StylingManager, 
        history_manager: HistoryManager,
        log_viewer: LogViewer, 
        entity_type: str, 
        entity_id: str
    ):
        super().__init__()
        
        self.styling_manager = styling_manager
        self.history_manager = history_manager

        self.setWindowTitle("Service Request Logs")
        self.resize(600, 300)
        self.setStyleSheet(self.styling_manager.dialog_style())

        self.entity_type = entity_type
        self.entity_id = entity_id
        
        self.log_viewer = log_viewer 
        
        layout = QVBoxLayout()
       
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Entity#", "Date of Export", "Log"])
        self.tree.setColumnWidth(0, 100)
        self.tree.setColumnWidth(1, 150)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
        self.load_tree()
        
    def load_tree(self):
        
        self.tree.clear()
        self.history = self.history_manager.all_history
        config_history = None

        match self.entity_type:
            case "sr_num":
                config_history  = [h for h in self.history.values() if h["sr_num"] == self.entity_id]
            case "config":
                config_history  = [h for h in self.history.values() if h["config"] == self.entity_id]

        if not config_history:
            QMessageBox.information(self, "Export Logs", "No Service Request registered for this configuration")
            return
        
        for items in config_history:
            
            date_of_export = items.get("date_extracted", "")
            export_log = items.get("extraction_log", "")

            match self.entity_type:
                case "config":
                    en_identifier = items.get("sr_num", "")
                case "sr_num":
                    en_identifier = items.get("config", "")
                                        
            item = QTreeWidgetItem([en_identifier, date_of_export, ''])
            self.tree.addTopLevelItem(item)
            
            log_preview_btn = QPushButton()
            log_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            log_preview_btn.setFlat(True)
            log_preview_btn.clicked.connect(lambda _, e_log = export_log : self.show_log(e_log))
            
            self.tree.setItemWidget(item, 2, log_preview_btn)
            
        self.exec_()
    
    def show_log(self, export_log): 
        self.log_viewer(self.styling_manager, export_log).exec_()    
            


