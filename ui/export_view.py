from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QComboBox, 
    QListView, QMessageBox, QDialog, QStyle, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread
from utils.styled_input_dialog import SingleLineInputDialog
from utils.log_viewer import LogViewer, TreePopUp
from utils.selector_dialog import SelectorDialog
from utils.permission_dialog import PermissionDialog
from core.executors.executables import ExtractionWorker

from core.models.data_models import (
    NewSRPayload, UpdateSRPayload, 
    RemoveSRPayload, UpdateSRConfigPayload,
    ReportPayload
)

from datetime import datetime
from typing import TYPE_CHECKING
import logging
import os

if TYPE_CHECKING:
    from core.managers.export_manager import ExportManager
    from core.managers.connection_manager import ConnectionManager
    from core.managers.query_manager import QueryManager
    from core.managers.history_manager import HistoryManager
    from core.managers.preset_manager import PresetManager
    from core.managers.export_configuration_manager import ExportConfigManager


logger = logging.getLogger(__name__)

class ExportsTab(QWidget):
    def __init__(self, 
            export_manager: ExportManager,
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
        
        self.connection_manager = connection_manager
        self.styling_manager = styling_manager
        self.query_manager = query_manager
        self.presets_manager = presets_manager
        self.history_manager = history_manager
        self.export_configurations_manager = export_configurations_manager
        self.export_manager = export_manager
        
        layout = QVBoxLayout()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Service Request #', 'Configuration', 'Extracted On', 'Extraction Log'])
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
        self.sr_configurations = self.export_manager.all_sr_configs
        self.connections = self.connection_manager.all_connections
        self.db_clients = self.connection_manager.all_clients
        self.queries = self.query_manager.all_queries
        
        
        layout.addWidget(self.tree)
        layout.addLayout(button_bar)
        
        self.setLayout(layout)
        
        self.load_sr_configs()
        self.export_manager.sr_config_updated.connect(self.load_sr_configs)
    
    def load_sr_configs(self):

        try:

            self.tree.clear()
            config_map = self.export_configurations_manager.config_name_id_map
            all_export_configs = config_map.keys()
            
            for sr_id, sr_config_items in self.sr_configurations.items():

                    sr_num = sr_config_items.get('sr_num', '')
                    config_name = sr_config_items.get('config_name', '')
                    extraction_date = self.history_manager.get_last_extracted("sr_num", sr_num) 

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

        except Exception as e:
                
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
    def show_sr_logs(self):

        try:
            
            sr_num = self.tree.currentItem().text(0)
            self.logs_preview_tree = TreePopUp(self.styling_manager, self.history_manager, LogViewer, "sr_num", sr_num)

        except Exception as e:
                
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
    def new_extraction(self):

        try:

            export_configs = self.export_configurations_manager.config_names

            while True:

                sr_num, ok1 = SingleLineInputDialog(
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

                new_sr_num, ok1 = SingleLineInputDialog(
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
            
            p_dialog = None

            try:
                                        
                msg_str = f"Are you sure to remove the configuration...?"
                p_dialog = PermissionDialog(msg_str, self.styling_manager)
                action = p_dialog.exec()
                if not action:
                    return

            finally:

                if p_dialog is not None:
                    p_dialog.deleteLater()

            self.export_manager.remove_sr(remove_sr_payload)

            QMessageBox.information(self, "Information", "SR removed successfully...")

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

    
    def perform_extraction(self):

        try:

            current_item = self.tree.currentItem()

            if not current_item:
                QMessageBox.warning(
                    self,
                    'Export',
                    'Select an SR to proceed!'
                )
                return

            timestamp = datetime.now()
            date_today = timestamp.strftime('%d%m%Y')

            sr_num = current_item.text(0)
            sr_id = current_item.data(0, Qt.ItemDataRole.UserRole)

            sr_name = f'mftbcffr_{sr_num}'
            base_folder_name = f'export_{sr_name}_{date_today}'
            base_folder_path = os.path.join(self.BASE_DIR, base_folder_name)

            if not os.path.exists(base_folder_path):
                os.makedirs(base_folder_path, exist_ok=True)

            export_config_selector = self.tree.itemWidget(current_item, 1)
            config_name = export_config_selector.currentText()
            config_id = self.export_configurations_manager.get_config_id(config_name)

            presets = self.export_configurations_manager.get_presets(config_name)       
            preset_items = self.presets_manager.get_preset_items(presets)            
            
            queries = self.queries            
            db_clients = self.db_clients

            p_dialog = None

            try:
                
                msg_str = f'Execution procedure for configuration : {config_name} for SR# : {sr_num}'
                p_dialog = PermissionDialog(msg_str, self.styling_manager)
                action = p_dialog.exec()
                if not action:
                    return

            finally:

                if p_dialog is not None:

                    p_dialog.deleteLater()

            
            logger.info(f'Execution started for configuration : {config_name} || SR# : {sr_num}')
            start_time = datetime.now()
            
            self.thread = QThread()

            self.worker = ExtractionWorker(
                preset_items, 
                queries, 
                db_clients,
                base_folder_path
            )
            
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)

            self.worker.error.connect(self.on_error)
            
            self.worker.finished.connect(
                lambda 
                report, 
                sr_id = sr_id, 
                config_id = config_id,
                start_time = start_time 
                : self.on_extraction_finished(
                    report, sr_id, config_id, start_time
                )
            )
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            self.thread.start()

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    def on_error(self, e):
        
        logger.error(f"{type(e).__name__}: {e}", exc_info=True)
        user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
        QMessageBox.critical(self, "Error", user_msg)

    def on_extraction_finished(self, report, sr_id, config_id, start_time):
        
        try:

            end_time = datetime.now()
            logger.info('Execution Complete ......... Records successfully exported.')
            logger.info(f'Time taken : {end_time - start_time}')

            config_name = self.export_configurations[config_id]["name"]
            sr_num = self.sr_configurations[sr_id]["sr_num"]

            new_report_payload = ReportPayload(
                sr_id = sr_id,
                sr_num = sr_num,
                config_id = config_id,
                config_name = config_name,
                status = "Completed",
                start_time = start_time,
                end_time = end_time,
                report = {
                    "logs": report
                }

            )

            self.history_manager.add_report(new_report_payload)
            self.export_manager.sr_config_updated.emit()

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
