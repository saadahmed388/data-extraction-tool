from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QMessageBox, QStyle, QHBoxLayout,
)

<<<<<<< HEAD
=======
from PyQt5.QtCore import Qt

from core.data_models import (
    NewConfigPayload, UpdateConfigPayload, 
    RemoveConfigPayload, UpdateConfigPresetListPayload
)

>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
from utilities.checkable_box import CheckableComboBox
from utilities.utils import TreePopUp, LogViewer
from typing import TYPE_CHECKING

import logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.managers.query_manager import QueryManager
    from core.managers.history_manager import HistoryManager
    from core.managers.preset_manager import PresetManager
    from core.managers.export_configuration_manager import ExportConfigManager

class ExportConfigsTab(QWidget):
    def __init__(self, 
            export_configurations_manager: ExportConfigManager,
            query_manager: QueryManager, 
            history_manager: HistoryManager, 
            presets_manager: PresetManager, 
            styling_manager
        ):

        super().__init__()
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
        self.rename_config_btn = QPushButton('Rename Configuration')
        self.remove_config_btn = QPushButton('Remove Configuration')
        self.new_config_btn.clicked.connect(self.new_configuration)
        self.rename_config_btn.clicked.connect(self.update_configuration)
        self.remove_config_btn.clicked.connect(self.remove_configuration)
        button_bar.addWidget(self.new_config_btn)
        button_bar.addWidget(self.rename_config_btn)
        button_bar.addWidget(self.remove_config_btn)
        self.new_config_btn.setStyleSheet(self.styling_manager.button_style())        
        self.rename_config_btn.setStyleSheet(self.styling_manager.button_style())
        self.remove_config_btn.setStyleSheet(self.styling_manager.button_style())
        
        self.export_configurations = self.export_configurations_manager.all_configs
        self.presets = self.presets_manager.all_presets
        
        layout.addWidget(self.tree)
        layout.addLayout(button_bar)
        
        self.setLayout(layout)
        
        self.load_export_configs()
        self.export_configurations_manager.export_configs_updated.connect(self.load_export_configs)
        self.presets_manager.presets_list_updated.connect(self.load_export_configs)
       
    def load_export_configs(self):

        try:
            self.tree.clear()        
            self.export_configurations = self.export_configurations_manager.all_configs
            preset_name_id_map = self.presets_manager.preset_name_id_map

            if not self.export_configurations:
                return
            
            for config_id, config_items in self.export_configurations.items():

                config_name = config_items["name"] 
                last_extracted_on = self.get_last_extracted(config_name)

                item = QTreeWidgetItem([config_name, '', last_extracted_on, ''])
                item.setData(0, Qt.ItemDataRole.UserRole, config_id)

                all_presets = preset_name_id_map.keys()
                selected_presets = config_items["presets"].values()
                
                self.export_configs_selector = CheckableComboBox(all_presets, selected_presets, preset_name_id_map)
                self.export_configs_selector.item_pressed.connect(self.update_config_preset_list)
                
                self.sr_logs_btn = QPushButton()
                self.sr_logs_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                self.sr_logs_btn.setFlat(True)
                self.sr_logs_btn.clicked.connect(self.show_sr_logs)
                
                self.tree.addTopLevelItem(item)
                self.tree.setItemWidget(item, 1, self.export_configs_selector)
                self.tree.setItemWidget(item, 3, self.sr_logs_btn)

        except Exception as e:
            
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
                            
    def new_configuration(self):
        try:

            name, ok1 = QInputDialog.getText(self, 'Configuration Name', 'Enter Configuration Name:')
            if not ok1 or not name:
                return            

            new_config_payload = NewConfigPayload(
                name=name
            )

            self.export_configurations_manager.new_export_config(new_config_payload)

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    
    def update_configuration(self):

        try:

            currentItem = self.tree.currentItem()
            old_name = currentItem.text(0)

            export_id = currentItem.data(0, Qt.ItemDataRole.UserRole)

            new_name, ok1 = QInputDialog.getText(self, 'Configuration Name', 'Enter New Configuration Name:', text = old_name)
            if not ok1 or not new_name:
                return            

            update_config_payload = UpdateConfigPayload(
                id=export_id,
                old_name=old_name,
                new_name=new_name
            )

            self.export_configurations_manager.update_export_config(update_config_payload)

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
    def remove_configuration(self):

        try:
            currentItem = self.tree.currentItem()
            config_id = currentItem.data(0, Qt.ItemDataRole.UserRole)
            config_name = currentItem.text(0)

            remove_config_payload = RemoveConfigPayload(
                id=config_id,
                name=config_name
            )

            self.export_configurations_manager.remove_export_config(remove_config_payload)

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def update_config_preset_list(self, payload: dict):
        
        try:

            item = self.tree.currentItem()
            config_id = item.data(0, Qt.ItemDataRole.UserRole)
            
            update_config_preset_list_payload = UpdateConfigPresetListPayload(
                config_id = config_id,
                preset_list = payload.get("list", {}),
                preset_name = payload.get("item_name", ""),
                preset_id = payload.get("item_id", ""),
                mode = payload.get("mode", "")
            )
            
            self.export_configurations_manager.update_config_preset_list(update_config_preset_list_payload)

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e} <br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
        
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
        
    