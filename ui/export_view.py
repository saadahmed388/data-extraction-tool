<<<<<<< HEAD
=======
from __future__ import annotations

>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QComboBox, 
    QListView, QLabel, QDialogButtonBox, QMessageBox, QDialog, QStyle, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread
from utilities.custom_widgets import StyledInputDialog
<<<<<<< HEAD
from utilities.utils import LogViewer, TreePopUp
from utilities.executables import ExtractionWorker

from datetime import datetime
=======
from utilities.utils import LogViewer, TreePopUp, SelectorDialog
from utilities.executables import ExtractionWorker

from core.data_models import (
    NewSRPayload, UpdateSRPayload, 
    RemoveSRPayload, UpdateSRConfigPayload
)

from datetime import datetime
from typing import TYPE_CHECKING, Dict
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
import regex as re
import logging
import time
import os
<<<<<<< HEAD
=======

if TYPE_CHECKING:
    from core.managers.export_manager import ExportManager
    from core.managers.connection_manager import ConnectionManager
    from core.managers.query_manager import QueryManager
    from core.managers.history_manager import HistoryManager
    from core.managers.preset_manager import PresetManager
    from core.managers.export_configuration_manager import ExportConfigManager
    from core.db_client import DBClient

>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)

logger = logging.getLogger(__name__)

class ExportsTab(QWidget):
    def __init__(self, 
            export_manager: ExportManager,
            db_clients: Dict[str, DBClient], 
            connection_manager: ConnectionManager, 
            query_manager: QueryManager, 
            history_manager: HistoryManager, 
            presets_manager: PresetManager, 
            export_configurations_manager: ExportConfigManager, 
            styling_manager
        ):
        super().__init__()
        self.BASE_DIR = 'exports'
        if not os.path.exists(self.BASE_DIR):
            os.makedirs(self.BASE_DIR, exist_ok = True)
        
        self.db_clients = db_clients
        self.connection_manager = connection_manager
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
        self.modify_sr_btn.clicked.connect(self.update_extraction)
        self.remove_sr_btn.clicked.connect(self.remove_extraction)
        self.export_btn.clicked.connect(self.perform_extraction)
        button_bar.addWidget(self.new_sr_btn)
        button_bar.addWidget(self.modify_sr_btn)
        button_bar.addWidget(self.remove_sr_btn)
        button_bar.addWidget(self.export_btn)
        self.new_sr_btn.setStyleSheet(self.styling_manager.button_style())
        self.modify_sr_btn.setStyleSheet(self.styling_manager.button_style()) 
        self.remove_sr_btn.setStyleSheet(self.styling_manager.button_style()) 
        self.export_btn.setStyleSheet(self.styling_manager.button_style()) 
        
        self.export_configurations = self.export_configurations_manager.all_configs
        self.presets = self.presets_manager.all_presets
        self.sr_configurations = self.export_manager.all_exports
        self.connections = self.connection_manager.all_connections
        self.queries = self.query_manager.all_queries
        
        layout.addWidget(self.tree)
        layout.addLayout(button_bar)
        
        self.setLayout(layout)
        
        self.load_sr_configs()
        self.export_manager.exports_updated.connect(self.load_sr_configs)
    
    def load_sr_configs(self):
        self.tree.clear()
        config_map = self.export_configurations_manager.config_name_id_map
        all_export_configs = config_map.keys()
        
        for sr_id, sr_config_items in self.sr_configurations.items():

                sr_num = sr_config_items.get('sr_num', '')
                config_name = sr_config_items.get('config_name', '')
                extraction_date = sr_config_items.get('extracted_on', "No Extractions Yet")
                extraction_log = sr_config_items.get('extraction_log', '')

                item = QTreeWidgetItem([sr_num, config_name, extraction_date, ''])
                item.setData(0, Qt.ItemDataRole.UserRole, sr_id)
                self.tree.addTopLevelItem(item)
                
                export_config_selector = QComboBox()
                export_config_selector.setView(QListView())
                export_config_selector.setObjectName('export_config_selector')
                export_config_selector.setAttribute(Qt.WA_StyledBackground, True)
                export_config_selector.setStyleSheet(self.styling_manager.selector_box_style('export_config_selector'))
                export_config_selector.view().setStyleSheet(self.styling_manager.selector_style())
                export_config_selector.addItem('No Selection')
                export_config_selector.addItems(all_export_configs)
                index = export_config_selector.findText(config_name)
                
                if index!= (-1):
                    export_config_selector.setCurrentIndex(index)

                export_config_selector.currentTextChanged.connect(self.update_config)
                
                self.tree.setItemWidget(item, 1, export_config_selector)
                
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                preview_btn.clicked.connect(self.show_sr_logs)
                
                self.tree.setItemWidget(item, 3, preview_btn)
    
    def show_sr_logs(self):
        sr_num = self.tree.currentItem().text(0)
        self.logs_preview_tree = TreePopUp(None, self.styling_manager, self.history_manager, LogViewer, selected_sr=sr_num)
    
    def new_extraction(self):

        try:

            export_configs = self.export_configurations_manager.config_names

            while True:

                sr_num, ok1 = StyledInputDialog(
                    'Service Request Number', 
                    'Enter SR# ( 4- 5 digits )'
                ).get_text()
                
                if not ok1 or not sr_num:
                    return

                if not (sr_num.isdigit() and 4 <= len(sr_num) <= 5):
                    QMessageBox.warning(self, "SR number guide", "Entered number is not within the accepted limits!!")
                    continue

                sr_num = sr_num.strip()

                if sr_num in self.export_manager.sr_nums:
                    QMessageBox.warning(self, "Warning", "SR Number already exists. Please enter a new number.!!")
                    continue

                config_selection_box = SelectorDialog("Select configuration", "Select an export config:", export_configs)
                
                try:
                    if config_selection_box.exec_() == QDialog.Rejected:
                        return

                    selected_config = config_selection_box.get_selected_item()

                finally:
                    config_selection_box.deleteLater()

                selected_config_id = self.export_configurations_manager.get_config_id(selected_config)

                new_sr_payload = NewSRPayload(
                    sr_num = sr_num,
                    export_config_id = selected_config_id,
                    export_config_name = selected_config
                )
                
                self.export_manager.new_export_sr(new_sr_payload) 
                return

        except Exception as e:
            
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
    def update_extraction(self):

        try:

            current_item = self.tree.currentItem()

            sr_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            old_sr_num = current_item.text(0)
                    
            while True:

                new_sr_num, ok1 = StyledInputDialog(
                    'Service Request Number', 
                    'Enter SR# ( 4- 5 digits )'
                ).get_text()
                
                if not ok1 or not new_sr_num:
                    return

                if not (new_sr_num.isdigit() and 4 <= len(new_sr_num) <= 5):
                    QMessageBox.warning(self, "SR number guide", "Entered number is not within the accepted limits!!")
                    continue

                new_sr_num = new_sr_num.strip()

                if new_sr_num in self.export_manager.sr_nums:
                    QMessageBox.warning(self, "Warning", "SR Number already exists. Please enter a new number.!!")
                    continue

                update_sr_payload = UpdateSRPayload(
                    sr_id = sr_id,
                    old_sr_num = old_sr_num,
                    new_sr_num = new_sr_num
                )
                    
                self.export_manager.update_export_sr(update_sr_payload)
                break

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    
    def remove_extraction(self):

        try:

            current_item = self.tree.currentItem()

            sr_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            sr_num = current_item.text(0)

            remove_sr_payload = RemoveSRPayload(
                sr_id = sr_id,
                sr_num = sr_num
            )
                
            self.export_manager.remove_sr(remove_sr_payload)

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def update_config(self):
    
        try:
    
            current_item = self.tree.currentItem()
            sr_id = current_item.data(0, Qt.ItemDataRole.UserRole)

            export_config_selector = self.tree.itemWidget(current_item, 1)
            selected_config = export_config_selector.currentText()
            selected_config_id = self.export_configurations_manager.get_config_id(selected_config)

            update_sr_config_payload = UpdateSRConfigPayload(
                sr_id = sr_id,
                export_config_id = selected_config_id,
                export_config_name = selected_config 
            )

            self.export_manager.update_export_sr_config(update_sr_config_payload)

        except Exception as e:
        
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def dynamic_save(self):
        current_item = self.tree.currentItem()
        export_config_selector = self.tree.itemWidget(current_item, 1)
        selected_config = export_config_selector.currentText()
        sr_num = current_item.text(0)
        self.sr_configurations[sr_num]['config_name'] = selected_config
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
            QMessageBox.warning(
                self,
                'Export',
                'Select a configuration to proceed!'
            )
            return

        timestamp = datetime.now()
        date_today = timestamp.strftime('%d%m%Y')

        sr_num = current_item.text(0)
        sr_name = f'mftbcffr_{sr_num}'
        base_folder_name = f'export_{sr_name}_{date_today}'
        base_folder_path = os.path.join(self.BASE_DIR, base_folder_name)

        if not os.path.exists(base_folder_path):
            os.makedirs(base_folder_path, exist_ok=True)

        export_config_selector = self.tree.itemWidget(current_item, 1)
        selected_config = export_config_selector.currentText()
        preset_list = self.export_configurations[selected_config]['preset_list']
        sql_list = self.queries
        self.info_list = []
    
        msg_str = f'Execution procedure for configuration : {selected_config} for SR# : {sr_num}'
        
        if not self.show_execution_dialog(msg_str, self.styling_manager).exec():
            return
        logger.info(f'Execution started for configuration : {selected_config} || SR# : {sr_num}')
        start_time = time.time()
        self.thread = QThread()
        self.worker = ExtractionWorker(preset_list, self.presets, base_folder_path, sql_list, self.db_clients)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda il, st=start_time, srn=sr_num, scon=selected_config: self.on_extraction_finished(st, il, srn, scon))
     
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
        print('\n')

    def on_extraction_finished(self, start_time, info_list, sr_num, selected_config):
        end_time = time.time()
        logger.info('Execution Complete ......... Records successfully exported.')
        logger.info(f'Time taken : {end_time - start_time}')
        self.info(info_list)
        self.add_to_history(sr_num, selected_config, info_list)
        self.update_sr_configurations(sr_num, info_list)
        self.update_export_configuration(selected_config)

    def add_to_history(self, sr_num, selected_config, info_list):
        self.history_manager.add_history(sr_num, selected_config, info_list)

    def update_sr_configurations(self, sr_num, extraction_log):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sr_configurations[sr_num]['extracted_on'] = timestamp
        self.sr_configurations[sr_num]['extraction_log'] = extraction_log
        self.export_manager.save_exports()

    def update_export_configuration(self, selected_config):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.export_configurations[selected_config]['extracted_on'] = timestamp
        self.export_configurations_manager.save_export_configs()

    def async_info(self, msg_text):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Execution Started')
        msg.setText(msg_text)
        msg.show()

    def show_log(self, styling_manager, extraction_log, LogViewer):
        self.log_viewer = LogViewer(styling_manager, extraction_log)
        self.log_viewer.exec_()

    def info(self, info_list):
        if not isinstance(info_list, list):
            info_list = [info_list]
        lines = []
        for item in info_list:
            env = item.get('env', 'Unknown Env')
            sql_name = item.get('sql_name', 'Unknown SQL')
            record_count = item.get('record_count', 'N/A')
            lines.append(f'Environment: {env}\nSQL: {sql_name}\nRecord Count: {record_count}')
        message = '\n\n'.join(lines)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Execution Summary')
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    class show_execution_dialog(QDialog):
        def __init__(self, message_str, styling_manager):
            super().__init__()
            self.resize(300, 100)
            self.styling_manager = styling_manager
            self.setStyleSheet(self.styling_manager.dialog_style())
            layout = QVBoxLayout()
            label = QLabel(message_str + '\nPress Ok to proceed...', self)
            layout.addWidget(label)
            btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            btn_box.accepted.connect(self.accept)
            btn_box.rejected.connect(self.reject)
            layout.addWidget(btn_box)
            self.setLayout(layout)

    def toast(self, message, duration=3000):
        toast = QLabel(message, self)
        toast.setAlignment(Qt.AlignCenter)
        toast.setStyleSheet("""
                                QLabel
                                {                
                                    background-color: rgba(50, 50, 50, 180);
                                    color: white;
                                    padding: 12px 18px;
                                    border-radius: 8px;
                                    font-size: 12pt;
                                }
                            """)
        parent_rect = self.rect()
        toast.adjustSize()
        toast.move(parent_rect.center() + toast.width() // 2, parent_rect.center() + toast.y() - toast.height() // 2)
        toast.show()
        QTimer.singleShot(duration, toast.close)