from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt
from utilities.sql_formatting import SqlPreview
from datetime import datetime
from utilities.checkable_box import CheckableComboBox
from utilities.utils import TreePopUp, LogViewer

class ExportConfigsTab(QWidget):
    def __init__(self, db_config_manager, query_manager, styling_manager, history_manager, presets_manager, export_configurations_manager):
        super().__init__()
        self.db_config_manager = db_config_manager
        self.styling_manager = styling_manager
        self.query_manager = query_manager
        self.presets_manager = presets_manager
        self.history_manager = history_manager
        self.export_configurations_manager = export_configurations_manager
        
        
        layout = QVBoxLayout()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Configuration Name', 'Presets List', 'Last Extracted On', 'Extraction Logs'])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 200)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        
        button_bar = QHBoxLayout()
        self.new_config_btn = QPushButton('New Configuration')
        self.save_config_btn = QPushButton('Save Configuration')
        self.rename_config_btn = QPushButton('Rename Configuration')
        self.remove_config_btn = QPushButton('Remove Configuration')
        self.new_config_btn.clicked.connect(self.new_configuration)
        self.save_config_btn.clicked.connect(self.save_configuration)
        self.rename_config_btn.clicked.connect(self.rename_configuration)
        self.remove_config_btn.clicked.connect(self.remove_configuration)
        button_bar.addWidget(self.new_config_btn)
        button_bar.addWidget(self.save_config_btn)
        button_bar.addWidget(self.rename_config_btn)
        button_bar.addWidget(self.remove_config_btn)
        self.new_config_btn.setStyleSheet(self.styling_manager.button_style())
        self.save_config_btn.setStyleSheet(self.styling_manager.button_style())
        self.rename_config_btn.setStyleSheet(self.styling_manager.button_style())
        self.remove_config_btn.setStyleSheet(self.styling_manager.button_style())
        
        self.export_configurations = self.export_configurations_manager.get_all_configs()
        self.presets = self.presets_manager.get_all_presets()
        
        
        layout.addWidget(self.tree)
        layout.addLayout(button_bar)
        
        self.setLayout(layout)
        
        self.load_export_configs()
        self.export_configurations_manager.export_configs_updated.connect(self.load_export_configs)
        self.presets_manager.presets_updated.connect(self.load_export_configs)
       
    def load_export_configs(self):
        self.tree.clear()        
        self.export_configurations = self.export_configurations_manager.get_all_configs()
        if self.export_configurations:
            for config_name, config_items in self.export_configurations.items():
                last_extracted_on = self.get_last_extracted(config_name)
                item = QTreeWidgetItem([config_name, '', last_extracted_on])
                all_presets = self.presets.keys()
                checked_presets = config_items["preset_list"]
                self.export_configs_selector = CheckableComboBox()
                self.export_configs_selector.addCheckItems(all_presets, checked_presets)
                
                self.sr_logs_btn = QPushButton()
                self.sr_logs_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                self.sr_logs_btn.setFlat(True)
                self.sr_logs_btn.clicked.connect(self.show_sr_logs)
                
                self.tree.addTopLevelItem(item)
                self.tree.setItemWidget(item, 1, self.export_configs_selector)
                self.tree.setItemWidget(item, 3, self.sr_logs_btn)
                            
    def new_configuration(self):
        name, ok1 = QInputDialog.getText(self, 'Configuration Name', 'Enter Configuration Name:')
        if not ok1 or not name:
            return            
        self.export_configurations_manager.new_export_config(name)
    
    def rename_configuration(self):
        currentItem = self.tree.currentItem()
        old_name = currentItem.text(0)
        new_name, ok1 = QInputDialog.getText(self, 'Configuration Name', 'Enter New Configuration Name:', text = old_name)
        if not ok1 or not new_name:
            return            
        self.export_configurations_manager.rename_config(new_name, old_name)
        
    def save_configuration(self):
        currentItem = self.tree.currentItem()
        
        if currentItem is None:
            QMessageBox.warning(self, "Export Configuration", "Please select a configuration to save")
            return
            
        config_name = currentItem.text(0)
        export_configs_selector = self.tree.itemWidget(currentItem, 1)
        selected_configs = export_configs_selector.getChecked()
        self.export_configurations[config_name]["preset_list"] = selected_configs
        self.export_configurations_manager.save_export_configs()
    
    def remove_configuration(self):
        currentItem = self.tree.currentItem()
        config_name = currentItem.text(0)
        self.export_configurations_manager.delete_export_config(config_name)
        
    def show_sr_logs(self):
        config_name = self.tree.currentItem().text(0)
        self.logs_preview_tree = TreePopUp(config_name, self.styling_manager, self.history_manager, LogViewer)
        
    def get_last_extracted(self, config_name):       
        history = self.history_manager.get_all_history()
        date_list = [item["date_extracted"] for item in history if item["config"] == config_name]
        date_list.sort(reverse=True)
        if date_list:
            return date_list[0]
        else:
            return "No Extractions Yet"
        
    