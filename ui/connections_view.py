from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt


from utils.styled_input_dialog import SingleLineInputDialog
from utils.permission_dialog import PermissionDialog

from core.models.data_models import NewConnectionPayload, UpdateConnectionPayload, RemoveConnectionPayload
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.managers.connection_manager import ConnectionManager


logger = logging.getLogger(__name__)

class ConnectionsTab(QWidget):
    def __init__(
            self, 
            connection_manager: ConnectionManager, 
            styling_manager
        ):
        super().__init__()
        self.connection_manager = connection_manager
        self.styling_manager = styling_manager
        self.connections = []
        self.db_clients = self.connection_manager.db_clients
        
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        self.add_con_btn = QPushButton("Add Connection")
        self.mod_con_btn = QPushButton("Modify Connection")        
        self.rem_con_btn = QPushButton("Remove Connection")
        self.add_con_btn.setStyleSheet(self.styling_manager.button_style())
        self.mod_con_btn.setStyleSheet(self.styling_manager.button_style())
        self.rem_con_btn.setStyleSheet(self.styling_manager.button_style())
        btn_layout.addWidget(self.add_con_btn)
        btn_layout.addWidget(self.mod_con_btn)
        btn_layout.addWidget(self.rem_con_btn)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Activity State', 'Connection', 'Username', 'DSN'])
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
       
        layout.addWidget(self.tree)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.add_con_btn.clicked.connect(self.add_connection)
        self.mod_con_btn.clicked.connect(self.update_connection)
        self.rem_con_btn.clicked.connect(self.remove_connection)
        self.connection_manager.connections_updated.connect(self.load_connections)
        self.load_connections()
        
    def load_connections(self):

        self.tree.clear()
        self.connections = self.connection_manager.all_connections
        self.db_clients = self.connection_manager.all_clients
        env_list = self.connection_manager.connection_names

        for con_id, con_details in self.connections.items():

            id = con_id
            env = con_details["name"]
            username = con_details["user"]
            dsn = con_details["dsn"]

            item = QTreeWidgetItem(['', env, username, dsn])

            item.setData(1, Qt.ItemDataRole.UserRole, id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setTextAlignment(0, Qt.AlignCenter)
            item.setCheckState(0, Qt.Checked)

            if env not in env_list:
                item.setCheckState(0, Qt.Unchecked)
            
            self.tree.addTopLevelItem(item)
            
    def add_connection(self):

        try:
            name, ok1 = SingleLineInputDialog("Add Connection", "Enter connection name:").get_text()        
            if not ok1 or not name:
                return
            username, ok2 = SingleLineInputDialog("Username", "Enter Username:").get_text()
            if not ok2 or not username:
                return   
            password, ok3 = SingleLineInputDialog("Password", "Enter Password:").get_text()
            if not ok3 or not password:
                return            
            dsn, ok4 = SingleLineInputDialog("DSN", "Enter DSN:").get_text()
            if not ok4 or not dsn:
                return 
            
            name = name.strip()
            username = username.strip()
            password = password.strip()
            dsn = dsn.strip()

            new_connection_payload = NewConnectionPayload(
                name=name,
                user=username,
                password=password,
                dsn=dsn
            )
                
            self.connection_manager.add_connection(new_connection_payload)
   
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

            
    def remove_connection(self):

        try: 
            
            selected  = self.tree.currentItem()

            if not selected:
                QMessageBox.warning(self, "No Selection", "Please select a connection to remove.")
                return 

            connection_id = selected.data(1, Qt.ItemDataRole.UserRole)
            connection_name = selected.text(1)

            remove_connection_payload = RemoveConnectionPayload(
                id=connection_id,
                name=connection_name
            )

            p_dialog = None

            try:
                                        
                msg_str = f"Are you sure to remove the connection...?"
                p_dialog = PermissionDialog(msg_str, self.styling_manager)
                action = p_dialog.exec()
                if not action:
                    return

            finally:

                if p_dialog is not None:
                    p_dialog.deleteLater()

            self.connection_manager.remove_connection(remove_connection_payload)

            QMessageBox.information(self, "Information", "Connection removed")

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
        
    def update_connection(self):

        try:
            selected = self.tree.currentItem()

            if not selected:
                QMessageBox.warning(self, "No Selection", "Please select a connection to modify.")
                return  

            id = selected.data(1, Qt.ItemDataRole.UserRole)
            old_name = selected.text(1)
            old_username = selected.text(2)
            old_dsn = selected.text(3)
              
                    
            new_name, ok1 = SingleLineInputDialog("Connection Name", "Enter new name:", "N", old_name).get_text()
            if not ok1 or not new_name:
                return
            
            new_username, ok2 = SingleLineInputDialog("Edit Username", "Enter new username:", "N", old_username).get_text()
            if not ok2 or not new_username:
                return
                
            new_password, ok3 = SingleLineInputDialog("Edit Password", "Enter new password:", "N").get_text()
            if not ok3 or not new_password:
                return
                
            new_dsn, ok4 = SingleLineInputDialog("Edit DSN", "Enter new DSN:", "Y", old_dsn).get_text()
            if not ok4 or not new_dsn:
                return
            
            new_name = new_name.strip()
            new_username = new_username.strip()
            new_password = new_password.strip()
            new_dsn = new_dsn.strip()

            updated_connection_payload = UpdateConnectionPayload(
                id=id,
                name=new_name,
                user=new_username,
                password=new_password,
                dsn=new_dsn
            )

            self.connection_manager.update_connection(updated_connection_payload)

            QMessageBox.information(self, "Information", "Connection updated")
            
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
            
    def get_active_connections(self):

        try:

            QApplication.processEvents()
            self.active_connections = set()
            
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                if item.checkState(0) == Qt.Checked:
                    env_name = item.text(1)
                    self.active_connections.add(env_name)
            
            return self.active_connections

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

            
    
        
        
        
    