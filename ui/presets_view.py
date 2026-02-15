from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTreeWidget, QStackedWidget, QListView,
    QPushButton, QTextEdit, QListWidgetItem, QTableWidget, QComboBox, QTreeWidget, QInputDialog, QTreeWidgetItem
)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import json
import os


class PresetsTab(QWidget):
    def __init__(self, query_manager, db_configs_manager, styling_manager, presets_manager):
        super().__init__()
        self.query_manager = query_manager
        self.db_configs_manager = db_configs_manager
        self.styling_manager = styling_manager
        self.presets_manager = presets_manager
        self.queries = self.query_manager.get_all_queries()
        
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
        self.new_preset_btn.clicked.connect(self.new_preset)
        button_bar.addWidget(self.new_preset_btn)
        
        # Modify Name Button
        self.edit_name_btn = QPushButton("Rename")
        self.edit_name_btn.setStyleSheet(self.styling_manager.button_style())
        self.edit_name_btn.clicked.connect(self.edit_name)
        button_bar.addWidget(self.edit_name_btn)
        
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
        self.tree.setHeaderLabels(['Active', 'Connections', 'Query'])
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        right_layout.addWidget(self.tree)
        
        self.save_preset_btn = QPushButton("Save Preset")
        self.save_preset_btn.setStyleSheet(self.styling_manager.button_style())
        self.save_preset_btn.clicked.connect(self.save_preset)
        right_layout.addWidget(self.save_preset_btn)
        
        self.delete_preset_btn = QPushButton("Delete Preset")
        self.delete_preset_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_preset_btn.clicked.connect(self.delete_preset)
        right_layout.addWidget(self.delete_preset_btn)
        
        button_bar = QHBoxLayout()
        button_bar.addWidget(self.save_preset_btn)
        button_bar.addWidget(self.delete_preset_btn)
        right_layout.addLayout(button_bar)
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)
        
        self.presets = self.presets_manager.get_all_presets()
        self.load_presets()
        
        self.preset_list.currentItemChanged.connect(self.load_preset_tree)
        self.presets_manager.presets_list_updated.connect(self.load_presets)
               
                
    def load_presets(self):        
        self.preset_list.clear()
        self.presets = self.presets_manager.get_all_presets() 
        for key in self.presets.keys():
            item = QListWidgetItem(key)
            self.preset_list.addItem(item)
            
    
    def load_preset_tree(self, preset_name):
        self.tree.clear()
        if preset_name is None:
            return            
        self.preset_name = preset_name.text()
        if not self.preset_name or self.preset_name not in self.presets.keys():
            self.presets_manager.new_preset(self.preset_name)

        for entry in self.presets[self.preset_name]:
            item = QTreeWidgetItem([
                "",
                entry["env"],
                entry["sql"]
            ])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked if entry["active"] else Qt.Unchecked)
            self.tree.addTopLevelItem(item)
            sql_selector = QComboBox()
            sql_selector.setView(QListView())
            sql_selector.setObjectName("sql_selector")
            sql_selector.setAttribute(Qt.WA_StyledBackground, True)
            sql_selector.setStyleSheet(self.styling_manager.selector_box_style("sql_selector"))
            sql_selector.view().setStyleSheet(self.styling_manager.selector_style())
            query_names = [q["name"] for q in self.queries]            
            sql_selector.addItems(query_names)
            index = sql_selector.findText(entry["sql"])
            if index != -1:
                sql_selector.setCurrentIndex(index)
            self.tree.setItemWidget(item, 2, sql_selector)
        
    def new_preset(self):
        
        name, ok1 = QInputDialog.getText(self, 'Preset Name', 'Enter Preset Name:')
        if not ok1 or not name:
            return
        
        item = QListWidgetItem(name)
        self.preset_list.addItem(item)
        self.presets_manager.new_preset(name)
        self.preset_list.setStyleSheet(self.styling_manager.list_style())
        
    def save_preset(self):
        
        preset_name = self.preset_list.currentItem().text()
        tree_state = []
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            active = item.checkState(0) == Qt.Checked
            env_name = item.text(1)
            sql_selector = self.tree.itemWidget(item, 2)
            selected_sql = sql_selector.currentText() if sql_selector else None
            
            new_entry = {
                            "active" : active,
                            "env" : env_name,
                            "sql" : selected_sql
                        }
            
            tree_state.append(new_entry)
            
        self.presets[preset_name] = tree_state
        self.presets_manager.save_preset()
    
    def delete_preset(self):
        preset_name = self.preset_list.currentItem().text()
        self.presets_manager.remove_preset(preset_name)
    
    def dynamic_save(self):
        
        return
    
    def edit_name(self):
        preset_name = self.preset_list.currentItem().text()        
        new_name, ok1 = QInputDialog.getText(self, 'Preset Name', 'Edit preset name:', text=preset_name)
        
        if ok1 and new_name.strip():         
            self.presets_manager.presets = self.rename_inplace(preset_name, new_name.strip())
            self.presets_manager.save_preset()
            current_row = self.preset_list.currentRow()
            self.load_presets()
            self.preset_list.setCurrentRow(current_row)

               
    def rename_inplace(self, old_name, new_name):
        new_dict = {}
        for k, v in self.presets.items():
            if k == old_name:
                new_dict[new_name] = v
            else:
                new_dict[k] = v
        return new_dict
        
            
            
        