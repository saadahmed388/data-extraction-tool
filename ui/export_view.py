from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog, QComboBox, QListView, QLabel, QDialogButtonBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from utilities.sql_formatting import SqlPreview
from utilities.custom_widgets import StyledInputDialog
from datetime import datetime
from utilities.utils import CheckableComboBox, LogViewer, TreePopUp
import regex as re
import pandas as pd
from datetime import datetime
import os

class ExportsTab(QWidget):
    def __init__(self, db_clients, db_config_manager, query_manager, styling_manager, history_manager, presets_manager, export_configurations_manager, export_manager):
        super().__init__()
        
        self.BASE_DIR = 'exports'
        if not os.path.exists(self.BASE_DIR):
            os.makedirs(self.BASE_DIR, exist_ok = True)
        
        self.db_clients = db_clients
        self.db_config_manager = db_config_manager
        self.styling_manager = styling_manager
        self.query_manager = query_manager
        self.presets_manager = presets_manager
        self.history_manager = history_manager
        self.export_configurations_manager = export_configurations_manager
        self.export_manager = export_manager
        
        layout = QVBoxLayout()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Service Request #', 'Configuration', 'Timestamp', 'Extraction Log'])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 200)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        
        button_bar = QHBoxLayout()
        self.new_sr_btn = QPushButton('New SR')
        self.modify_sr_btn = QPushButton('Modify SR')
        self.remove_sr_btn = QPushButton('Remove SR')
        self.export_btn = QPushButton('Export')
        self.new_sr_btn.clicked.connect(self.new_extraction)
        self.modify_sr_btn.clicked.connect(self.modify_extraction)
        self.remove_sr_btn.clicked.connect(self.remove_configuration)
        self.export_btn.clicked.connect(self.perform_extraction)
        button_bar.addWidget(self.new_sr_btn)
        button_bar.addWidget(self.modify_sr_btn)
        button_bar.addWidget(self.remove_sr_btn)
        button_bar.addWidget(self.export_btn)
        self.new_sr_btn.setStyleSheet(self.styling_manager.button_style())
        self.modify_sr_btn.setStyleSheet(self.styling_manager.button_style()) 
        self.remove_sr_btn.setStyleSheet(self.styling_manager.button_style()) 
        self.export_btn.setStyleSheet(self.styling_manager.button_style()) 
        
        self.export_configurations = self.export_configurations_manager.get_all_configs()
        self.presets = self.presets_manager.get_all_presets()
        self.sr_configurations = self.export_manager.get_all_exports()
        self.connections = self.db_config_manager.get_all_connections()
        self.queries = self.query_manager.get_all_queries()
        
        layout.addWidget(self.tree)
        layout.addLayout(button_bar)
        
        self.setLayout(layout)
        
        self.load_sr_configs()
        self.export_manager.exports_updated.connect(self.load_sr_configs)
    
    def load_sr_configs(self):
        self.tree.clear()
        self.sr_configurations = self.export_manager.get_all_exports()
        all_export_configs = self.export_configurations.keys() 
        if self.sr_configurations:
            for sr_num, sr_config_items in self.sr_configurations.items():
                config_name = sr_config_items.get("config_name", "")
                extraction_date = sr_config_items.get("extracted_on", "") 
                extraction_log = sr_config_items.get("extraction_log", "")
                
                item = QTreeWidgetItem([sr_num, config_name, extraction_date, '']) 
                self.tree.addTopLevelItem(item)
                
                export_config_selector = QComboBox()
                export_config_selector.setView(QListView())                
                export_config_selector.setObjectName("export_config_selector")
                export_config_selector.setAttribute(Qt.WA_StyledBackground, True)
                export_config_selector.setStyleSheet(self.styling_manager.selector_box_style("export_config_selector"))
                export_config_selector.view().setStyleSheet(self.styling_manager.selector_style())
                export_config_selector.addItem("No Selection")
                export_config_selector.addItems(all_export_configs)
                index = export_config_selector.findText(config_name)
                if index != -1:
                    export_config_selector.setCurrentIndex(index)
                export_config_selector.currentTextChanged.connect(self.dynamic_save)
                              
                self.tree.setItemWidget(item, 1, export_config_selector)
                
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                #preview_btn.clicked.connect(lambda _, s = self.styling_manager, e = extraction_log, l = LogViewer : self.show_log(s, e, l))
                preview_btn.clicked.connect(self.show_sr_logs)
                self.tree.setItemWidget(item, 3, preview_btn)
                
    def show_sr_logs(self):
        sr_num = self.tree.currentItem().text(0)
        self.logs_preview_tree = TreePopUp(None, self.styling_manager, self.history_manager, LogViewer, selected_sr = sr_num)
                
                            
    def new_extraction(self):
        sr_num = ''
        while True:
            sr_num, ok1 = StyledInputDialog('Service Request Number', 'Enter SR#:').get_text()
            #QInputDialog.getText(self, 'Service Request Number', 'Enter SR#:')
            if not ok1:
                return
            elif not re.fullmatch(r'\d+', sr_num) or len(sr_num) not in (4,5):
                QMessageBox.warning(self, "Invalid SR Number", "Please a valid SR #!!")
                continue
            else:
                break
  
        self.export_manager.new_export(sr_num)
    
    def save_extraction(self):
        currentItem = self.tree.currentItem()
        config_name = currentItem.text(0)
        self.export_manager.save_exports()
    
    def modify_extraction(self):
        current_item = self.tree.currentItem()
        old_sr_num = current_item.text(0)
        new_sr_num = ''
        while True:
            new_sr_num, ok1 = StyledInputDialog('Enter SR #','Enter New SR Number:', default_text = old_sr_num).get_text()
            #QInputDialog.getText(self, 'Enter SR #','Enter New SR Number:', text=old_sr_num)
            if not ok1:
                break
            elif not re.fullmatch(r'\d+', new_sr_num) or len(new_sr_num) not in (4,5):
                QMessageBox.warning(self, "Invalid SR Number", "Please enter a valid SR #!!")
                continue
            else:
                new_export_dict = self.modification_helper(old_sr_num, new_sr_num)
                self.export_manager.exports = new_export_dict
                self.export_manager.save_exports()
                break
                   
    def remove_configuration(self):
        currentItem = self.tree.currentItem()
        sr_num = currentItem.text(0)
        self.export_manager.remove_export(sr_num)
        
    def dynamic_save(self):
        current_item = self.tree.currentItem()
        export_config_selector = self.tree.itemWidget(current_item, 1)
        selected_config = export_config_selector.currentText()
        sr_num = current_item.text(0)
        self.sr_configurations[sr_num]["config_name"] = selected_config
        self.export_manager.save_exports()
        
    def modification_helper(self, old_sr_num, new_sr_num):
        new_dict = {}
        for k, v in self.sr_configurations.items():
            if k == old_sr_num:
                new_dict[new_sr_num] = v
            else:
                new_dict[k] = v
        return new_dict
        
    def perform_extraction(self):
                        
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Export", "Select a configuration to proceed!")
            return
        
        timestamp = datetime.now()
        date_today = timestamp.strftime("%d%m%Y")
        
        sr_num = current_item.text(0)
        sr_name = f"mftbcffr_{sr_num}"
            
        base_folder_name = f"export_{sr_name}_{date_today}"
        base_folder_path = os.path.join(self.BASE_DIR, base_folder_name)
        if not os.path.exists(base_folder_path):
            os.makedirs(base_folder_path, exist_ok = True)
                
        export_config_selector = self.tree.itemWidget(current_item, 1)
        selected_config = export_config_selector.currentText()
        
        preset_list = self.export_configurations[selected_config]["preset_list"]
        sql_list = self.queries
        info_list = []
        
        print('\n\n')
        print(f"......... Execution started of configuration : {selected_config} for SR# : {sr_num} .........")
        msg_str = f"Execution procedure for configuration : {selected_config} for SR# : {sr_num}"
        self.show_execution_dialog(msg_str, self.styling_manager)
          
        for preset in preset_list:
            for item in self.presets[preset]:
                if item["active"] == True:
                    env = item["env"]
                    sql_name = item["sql"]
                    sql_list_item = [item for item in sql_list if item["name"] == sql_name]

                    dbc_obj = self.db_clients[env]

                    class_folder_name = sql_list_item[0]["class"]
                    class_folder_path = os.path.join(base_folder_path, class_folder_name)
                    if not os.path.exists(class_folder_path):
                        os.makedirs(class_folder_path, exist_ok = True)
                        
                    file_name = f"{env}.csv"
                    file_path = os.path.join(class_folder_path, file_name)
                    
                    sql = sql_list_item[0]["sql"]

                                        
                    #self.executing_dialog = self.show_executing_dialog(env)
                    #self.executing_dialog.show()
                    print('\n\n')
                    print(f"......... Executing {sql_name} query of class {class_folder_name} belonging to preset {preset} on {env} .........")
                    rows, cols = dbc_obj.execute_select(sql)
                    df = pd.DataFrame(rows, columns = cols, dtype = str)
                    df.to_csv(file_path, index=False, encoding="utf-8")
                    record_count = len(rows)
                    print(df.head())
                    
                    print(f"......... Execution successful ......... Exported {record_count} rows .........")
                    
                    info_item = {"env":env, "sql_name":sql_name, "record_count":record_count}
                    info_list.append(info_item)

        self.add_to_history(sr_num, selected_config, info_list)
        self.update_sr_configurations(sr_num, info_list)
        self.update_export_configuration(selected_config)
               
        print('\n\n')
        print(f"......... Execution Complete ......... Records successfully exported .........")
        self.info(info_list)
        print('\n\n')            
                         
    
    def add_to_history(self, sr_num, selected_config, info_list):
        self.history_manager.add_history(sr_num, selected_config, info_list)
        
    def update_sr_configurations(self, sr_num, extraction_log):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sr_configurations[sr_num]["extracted_on"] = timestamp
        self.sr_configurations[sr_num]["extraction_log"] = extraction_log
        self.export_manager.save_exports()
                          
    def update_export_configuration(self, selected_config):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.export_configurations[selected_config]["extracted_on"] = timestamp
        self.export_configurations_manager.save_export_configs()
                          
    def async_info(self, msg_text):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Execution Started")
        msg.setText(msg_text)
        #msg.setStandardButtons(QMessageBox.Ok)
        msg.show()
    
    def show_log(self, styling_manager, extraction_log, LogViewer):
        self.log_viewer = LogViewer(styling_manager, extraction_log)
        self.log_viewer.exec_()
         
    def info(self, info_list):
        
        if not isinstance(info_list, list):
            info_list = [info_list]

        lines = []
        for item in info_list:
            env = item.get("env", "Unknown Env")
            sql_name = item.get("sql_name", "Unknown SQL")
            record_count = item.get("record_count", "N/A")
            lines.append(f"Environment: {env}\nSQL: {sql_name}\nRecord Count: {record_count}")

        message = "\n\n".join(lines)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Execution Summary")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    
     
        
    class show_execution_dialog(QDialog):
        def __init__(self, message_str, styling_manager):
            super().__init__()            
            self.setWindowTitle("Query Execution")
            self.setModal(True)
            self.resize(300, 100)
            self.styling_manager = styling_manager
            self.setStyleSheet(self.styling_manager.dialog_style())
            
            layout = QVBoxLayout()
            label = QLabel(message_str + "\nPress Ok to proceed...", self)            
            layout.addWidget(label)
             
            btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            btn_box.accepted.connect(self.accept)  
            btn_box.rejected.connect(self.reject)  
            layout.addWidget(btn_box)

            self.setLayout(layout)
            self.exec_()
       
                 
                 
    def toast(self, message, duration=3000):
        toast = QLabel(message, self)
        toast.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        toast.setAlignment(Qt.AlignCenter)
        toast.setStyleSheet(
            """
            QLabel {
                background-color: rgba(50, 50, 50, 180);
                color: white;
                padding: 12px 18px;
                border-radius: 8px;
                font-size: 12pt;
            }
            """
        )
        
        # Position at center of parent window
        parent_rect = self.rect()
        toast.adjustSize()
        toast.move(
            parent_rect.center().x() - toast.width() // 2,
            parent_rect.center().y() - toast.height() // 2
        )
        
        toast.show()

        # Auto-close after duration
        QTimer.singleShot(duration, toast.close)
