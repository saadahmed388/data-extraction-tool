from PyQt5.QtWidgets import (
                            QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, 
                            QComboBox, QListView, QTreeWidget, QMessageBox, QTreeWidgetItem,
                            QStyle
)
from utilities.stylesheets import StylingManager
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class StyledInputDialog(QDialog):
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
        self.result = self.exec_()
        text = self.input.text().strip()
        if self.caps.upper() == "Y":
            text = text.upper()
        return text, self.result == QDialog.Accepted


class CheckableComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setView(QListView())
        self.setModel(QStandardItemModel(self))
        self.checked = []
        self.styling_manager = StylingManager()
        self.setObjectName("export_configs_selector")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self.styling_manager.selector_box_style("export_configs_selector"))
        self.view().setStyleSheet(self.styling_manager.selector_style())
        self.view().pressed.connect(self.handleItemPressed)

    def addCheckItems(self, all_presets, checked_presets):
        for text in all_presets:
            item = QStandardItem(text)
            item.setFlags((item.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsTristate)            
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            if text in checked_presets:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.model().appendRow(item)

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        item.setFlags((item.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsTristate)
        if item.checkState():
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.updateText()

    def updateText(self):
        self.checked = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState():
                self.checked.append(item.text())
        self.setEditText(", ".join(self.checked))
        
    def getChecked(self):
        return self.checked


class TreePopUp(QDialog):
    def __init__(self, selected_config, styling_manager, history_manager, log_viewer, selected_sr = None):
        super().__init__()
        self.styling_manager = styling_manager
        self.history_manager = history_manager
        self.setWindowTitle("Service Request Logs")
        self.resize(600, 300)
        self.setStyleSheet(self.styling_manager.dialog_style())
        self.config_name = selected_config
        self.sr_num = selected_sr
        self.log_viewer = log_viewer 
        
        layout = QVBoxLayout()
       
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["SR#", "Date of Export", "Log"])
        self.tree.setColumnWidth(0, 100)
        self.tree.setColumnWidth(1, 150)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
        self.load_tree()
        
    def load_tree(self):
        
        self.tree.clear()
        self.history = self.history_manager.get_all_history()
        if not self.sr_num:
            config_history  = [h for h in self.history if h["config"] == self.config_name]
        else:
            print(self.sr_num)
            config_history  = [h for h in self.history if h["sr_num"] == self.sr_num]
        
        if config_history:
            for items in config_history:
                config_name = items.get("config", "")
                sr_num = items.get("sr_num", "")
                date_of_export = items.get("date_extracted", "")
                export_log = items.get("extraction_log", "")
                                            
                item = QTreeWidgetItem([sr_num, date_of_export, ''])
                self.tree.addTopLevelItem(item)
                
                log_preview_btn = QPushButton()
                log_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                log_preview_btn.setFlat(True)
                log_preview_btn.clicked.connect(lambda _, e_log = export_log : self.show_log(e_log))
                
                self.tree.setItemWidget(item, 2, log_preview_btn)
                
            self.exec_()
            
        else:
            QMessageBox.information(self, "Export Logs", "No Service Request registered for this configuration")
               
    def show_log(self, export_log):
        print("Showing")
        self.log_viewer(self.styling_manager, export_log).exec_()    
            
class LogViewer(QDialog):
    def __init__(self, styling_manager, export_log = None):
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
        
    