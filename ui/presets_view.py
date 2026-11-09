<<<<<<< HEAD
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTreeWidget, QListView,
    QPushButton, QListWidgetItem, QComboBox, QTreeWidget, QInputDialog, QTreeWidgetItem
)
from PyQt5.QtCore import Qt
from core.managers.query_manager import QueryManager
=======
from __future__  import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTreeWidget, QListView,
    QPushButton, QListWidgetItem, QComboBox, QTreeWidget, QInputDialog, QTreeWidgetItem,
    QInputDialog, QDialog, QMessageBox
)

from core.data_models import (
    NewPresetPayload, UpdatePresetPayload, RemovePresetPayload,
    NewPresetItemPayload, UpdatePresetItemPayload, RemovePresetItemPayload
)

import logging

from PyQt5.QtCore import Qt
from typing import TYPE_CHECKING
from utilities.utils import SelectorDialog
from  psycopg2.errors import UniqueViolation

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.managers.query_manager import QueryManager
    from core.managers.connection_manager import ConnectionManager
    from core.managers.preset_manager import PresetManager
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)

class PresetsTab(QWidget):
    def __init__(
            self, 
            presets_manager: PresetManager,
            connection_manager: ConnectionManager, 
            query_manager: QueryManager, 
            styling_manager, 
        ):
        super().__init__()
        self.presets_manager = presets_manager
        self.query_manager = query_manager
        self.connection_manager = connection_manager
        self.styling_manager = styling_manager
        self.queries = self.query_manager.all_queries
        
        # ==================== MAIN LAYOUT ====================
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # ==================== LEFT PANEL ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        
        #Top Button Bar
        button_bar = QHBoxLayout()

        # “New Preset” Button
        self.new_preset_btn = QPushButton("＋ New Preset")
        self.new_preset_btn.setStyleSheet(self.styling_manager.button_style())
        self.new_preset_btn.clicked.connect(self.add_preset)
        button_bar.addWidget(self.new_preset_btn)
        
        # Modify Name Button
        self.edit_name_btn = QPushButton("Rename")
        self.edit_name_btn.setStyleSheet(self.styling_manager.button_style())
        self.edit_name_btn.clicked.connect(self.update_preset)
        button_bar.addWidget(self.edit_name_btn)

        # Delete Preset Button
        self.delete_preset_btn = QPushButton("Delete Preset")
        self.delete_preset_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_preset_btn.clicked.connect(self.remove_preset)
        button_bar.addWidget(self.delete_preset_btn)
        
        left_layout.addLayout(button_bar)

        # Preset List (Vertical Tab List)
        self.preset_list = QListWidget()
        self.preset_list.setStyleSheet(self.styling_manager.list_style())
        left_layout.addWidget(self.preset_list, stretch=1)
        
        # ===================== RIGHT PANEL ====================
        
        right_panel =  QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
              
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Connections', 'Query'])
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        right_layout.addWidget(self.tree)

        # Add Preset Item button
        self.add_preset_item_btn = QPushButton("Add Preset Item")
        self.add_preset_item_btn.setStyleSheet(self.styling_manager.button_style())
        self.add_preset_item_btn.clicked.connect(self.add_preset_item)
        right_layout.addWidget(self.add_preset_item_btn)

        # Save Preset Button
        self.remove_preset_item_btn = QPushButton("Remove Preset Item")
        self.remove_preset_item_btn.setStyleSheet(self.styling_manager.button_style())
        self.remove_preset_item_btn.clicked.connect(self.remove_preset_item)
        right_layout.addWidget(self.remove_preset_item_btn)
        
        button_bar = QHBoxLayout()
        button_bar.addWidget(self.add_preset_item_btn)
        button_bar.addWidget(self.remove_preset_item_btn)
        right_layout.addLayout(button_bar)
        
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)
        
        self.presets = self.presets_manager.all_presets
        self.load_presets()
        
        self.preset_list.currentItemChanged.connect(self.load_preset_tree)
        self.presets_manager.preset_updated.connect(lambda x: self.load_preset_tree(x))
        self.connection_manager.connections_updated.connect(self.load_presets)
        self.presets_manager.presets_list_updated.connect(self.load_presets)
            
    def load_presets(self):

        try:

            self.preset_list.clear()
            self.presets = self.presets_manager.all_presets
            preset_list = self.presets_manager.preset_list

            for name, id in preset_list.items():
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, id)
                self.preset_list.addItem(item)
        
        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
            
    def load_preset_tree(self, preset_id, *args):

        connection_names = self.connection_manager.connection_names
        query_names = self.query_manager.query_names
        self.tree.clear()

        if preset_id is None:
            return            

        if isinstance(preset_id, QListWidgetItem):
            preset_id = preset_id.data(Qt.ItemDataRole.UserRole)

        preset_data =  self.presets.get(preset_id)
        if not preset_data:
            return

        entries = preset_data.get("items", {})

        for preset_item_id, preset_item in entries.items():

            item = QTreeWidgetItem([
                preset_item["env"],
                preset_item["sql"]
            ])

            item.setData(0, Qt.ItemDataRole.UserRole, preset_item_id)
        
            self.tree.addTopLevelItem(item)
            
            sql_selector = QComboBox()
            sql_selector.setView(QListView())
            sql_selector.setObjectName("sql_selector")
            sql_selector.setAttribute(Qt.WA_StyledBackground, True)
            sql_selector.setStyleSheet(self.styling_manager.selector_box_style("sql_selector"))
            sql_selector.view().setStyleSheet(self.styling_manager.selector_style())
            sql_selector.addItems(query_names)
            index = sql_selector.findText(preset_item["sql"])
            if index != -1:
                sql_selector.setCurrentIndex(index)
            sql_selector.setProperty("old_val", sql_selector.currentText())  
            sql_selector.currentTextChanged.connect(lambda text, itm=item, sltr=sql_selector, type="query": self.update_preset_item(text, itm, sltr, type)) 
            self.tree.setItemWidget(item, 1, sql_selector)

            connection_selector = QComboBox()
            connection_selector.setView(QListView())
            connection_selector.setObjectName("connection_selector")
            connection_selector.setAttribute(Qt.WA_StyledBackground, True)
            connection_selector.setStyleSheet(self.styling_manager.selector_box_style("connection_selector"))
            connection_selector.view().setStyleSheet(self.styling_manager.selector_style())         
            connection_selector.addItems(connection_names)
            index = connection_selector.findText(preset_item["env"])
            if index != -1:
                connection_selector.setCurrentIndex(index)
            connection_selector.setProperty("old_val", connection_selector.currentText())
            connection_selector.currentTextChanged.connect(lambda text, itm=item, sltr=connection_selector, type="connection": self.update_preset_item(text, itm, sltr, type)) 
            self.tree.setItemWidget(item, 0, connection_selector)
        
    def add_preset(self):

        try:
            
            name, ok1 = QInputDialog.getText(self, 'Preset Name', 'Enter Preset Name:')
            if not ok1 or not name:
                return

            new_preset_payload = NewPresetPayload(
                name=name
            )

            self.presets_manager.add_preset(new_preset_payload)
           

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def remove_preset(self):

        try:
            
            preset = self.preset_list.currentItem()

            preset_id = preset.data(Qt.ItemDataRole.UserRole)
            preset_name = preset.text()

            remove_preset_payload = RemovePresetPayload(
                id=preset_id,
                name=preset_name
            )

            self.presets_manager.remove_preset(remove_preset_payload)

        except Exception as e:
            
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
    def update_preset(self):

        try:

            preset = self.preset_list.currentItem()

            preset_id = preset.data(Qt.ItemDataRole.UserRole)
            old_name = preset.text()        
            
            new_name, ok = QInputDialog.getText(self, 'Preset Name', 'Edit preset name:', text=old_name)
            new_name = new_name.strip()

            if not ok or not new_name:
                return 

            update_preset_payload = UpdatePresetPayload(
                id=preset_id,
                old_name=old_name,
                new_name=new_name
            )

            current_row = self.preset_list.currentRow()
            self.presets_manager.update_preset(update_preset_payload)
            self.preset_list.setCurrentRow(current_row)

        except Exception as e:
            
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)


    def add_preset_item(self):

        try:

            connections = self.connection_manager.connection_names
            queries = self.query_manager.query_names

            connection_id_map = self.connection_manager.connection_name_id_map
            query_id_map = self.query_manager.query_name_id_map
            preset_id_map = self.presets_manager.preset_name_id_map

            connection_selection_box = SelectorDialog("Select connection", "Select a connection:", connections)
            query_selection_box = SelectorDialog("Select query", "Select a query:", queries)
            
            if connection_selection_box.exec_() == QDialog.Rejected:
                return
            
            if query_selection_box.exec_() == QDialog.Rejected:
                return

            preset_name = self.preset_list.currentItem().text()
            con_name = connection_selection_box.get_selected_item()
            query_name = query_selection_box.get_selected_item()

            preset_id = preset_id_map[preset_name]
            con_id = connection_id_map[con_name]
            query_id = query_id_map[query_name]

            new_preset_item_payload = NewPresetItemPayload(
                preset_id=preset_id,
                con_id=con_id,
                query_id=query_id,
                preset_name=preset_name,
                con_name=con_name,
                query_name=query_name
            )

            self.presets_manager.add_preset_item(new_preset_item_payload)

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def update_preset_item(self, text: str, preset_item: QTreeWidgetItem, selector: QComboBox, preset_item_type: str):
        try:

            if preset_item_type == "connection":
                curr_env_name = text
                prev_env_name = selector.property("old_val")
                curr_query_name = preset_item.text(1)
                prev_query_name = preset_item.text(1)

            if preset_item_type == "query":
                curr_query_name = text
                prev_query_name = selector.property("old_val")
                curr_env_name = preset_item.text(0)
                prev_env_name = preset_item.text(0)

            preset = self.preset_list.currentItem()
            preset_name = preset.text()
            preset_id = preset.data(Qt.ItemDataRole.UserRole)
            preset_item_id = preset_item.data(0, Qt.ItemDataRole.UserRole)

            if curr_env_name == prev_env_name and curr_query_name == prev_query_name:
                return

            connection_id_map = self.connection_manager.connection_name_id_map
            query_id_map = self.query_manager.query_name_id_map
            preset_id_map = self.presets_manager.preset_name_id_map

            con_id = connection_id_map[curr_env_name]
            query_id = query_id_map[curr_query_name]

            update_preset_item_payload = UpdatePresetItemPayload(
                preset_item_id=preset_item_id,
                preset_id=preset_id,
                con_id=con_id,
                query_id=query_id,
                preset_name=preset_name,
                con_name=curr_env_name,
                query_name=curr_query_name   
            )

            self.presets_manager.update_preset_item(update_preset_item_payload)
        
        except Exception as e:
            selector.setCurrentText(selector.property())
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)


    def remove_preset_item(self):
        try:
            preset = self.preset_list.currentItem()
            preset_name = preset.text()
            preset_id = preset.data(Qt.ItemDataRole.UserRole)
            preset_item_id = self.tree.currentItem().data(0, Qt.ItemDataRole.UserRole)

            if not preset_name:
                return

            remove_preset_item_payoad = RemovePresetItemPayload(
                preset_name=preset_name,
                preset_id=preset_id,
                preset_item_id=preset_item_id
            )

            self.presets_manager.remove_preset_item(remove_preset_item_payoad)

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
 