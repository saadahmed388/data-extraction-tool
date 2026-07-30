from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
from utilities.custom_widgets import StyledInputDialog
from PyQt5.QtCore import Qt
from core.db_client import DBClient
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.managers.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class ConnectionsTab(QWidget):
    def __init__(self, connection_manager: ConnectionManager, styling_manager):
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
        self.mod_con_btn.clicked.connect(self.modify_connection)
        self.rem_con_btn.clicked.connect(self.remove_connection)
        self.connection_manager.connections_updated.connect(self.load_connections)
        self.load_connections()
        
    def load_connections(self):

        self.tree.clear()
        self.connections = self.connection_manager.get_all_connections()
        self.db_clients = self.connection_manager.get_all_clients()

        for connection in self.connections:
            
            env = connection["name"]
            username = connection["user"]
            dsn = connection["dsn"]

            item = QTreeWidgetItem(['', env, username, dsn])
            
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setTextAlignment(0, Qt.AlignCenter)
            item.setCheckState(0, Qt.Checked)
            if env not in self.db_clients.keys():
                item.setCheckState(0, Qt.Unchecked)
            
            self.tree.addTopLevelItem(item)
            
    def add_connection(self):
        
        name, ok1 = StyledInputDialog("Add Connection", "Enter connection name:").get_text()        
        if not ok1 or not name:
            return
        username, ok2 = StyledInputDialog("Username", "Enter Username:").get_text()
        if not ok2 or not username:
            return   
        password, ok3 = StyledInputDialog("Password", "Enter Password:").get_text()
        if not ok3 or not password:
            return            
        dsn, ok4 = StyledInputDialog("DSN", "Enter DSN:").get_text()
        if not ok4 or not dsn:
            return 
        
        name = name.strip()
        username = username.strip()
        password = password.strip()
        dsn = dsn.strip()
                
        if not self.connection_manager.add_connection(name, username, password, dsn):
            QMessageBox.information(self, "Connection Window", f"Invalid Credentials...")
            return
        QMessageBox.information(self, "Connection Window", f"Connection Successful")

    
    def remove_connection(self):
        
        self.connection_manager.remove_connection(self.tree.currentItem().text(1))
    
    def modify_connection(self):
        
        selected = self.tree.currentItem()
        
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a connection to modify.")
            return
        
        old_name = selected.text(1)
        
        for c in self.connections:
            if c["name"] == old_name: 
                old_username = c["user"]
                old_password = c["password"]
                old_dsn = c["dsn"]
        
        new_name, ok1 = StyledInputDialog("Connection Name", "Enter new name:", "N", old_name).get_text()
        if not ok1 or not new_name:
            return
        
        if ok1 and self.check_name(new_name, old_name):
            QMessageBox.warning(self, "Name already exists", "Please choose another name.")
            return
        
        new_username, ok2 = StyledInputDialog("Edit Username", "Enter new username:", "N", old_username).get_text()
        if not ok2 or not new_username:
            return
            
        new_password, ok3 = StyledInputDialog("Edit Password", "Enter new password:", "N", old_password).get_text()
        if not ok3 or not new_password:
            return
            
        new_dsn, ok4 = StyledInputDialog("Edit DSN", "Enter new DSN:", "Y", old_dsn).get_text()
        if not ok4 or not new_dsn:
            return
        
        new_name = new_name.strip()
        new_username = new_username.strip()
        new_password = new_password.strip()
        new_dsn = new_dsn.strip()

        if not self.connection_manager.connect_modified(new_name, new_username, new_password, new_dsn, self.db_clients):
            QMessageBox.information(self, "Connection Window", f"Invalid Credentials...")
            return
        QMessageBox.information(self, "Connection Window", f"Connection Successful")

        for c in self.connections:
            if c["name"] == old_name:
                if ok1 and new_name:
                    c["name"] = new_name
                if ok2 and new_username:
                    c["user"] = new_username
                if ok3 and new_password:
                    c["password"] = new_password
                if ok4 and new_dsn:
                    c["dsn"] = new_dsn
                break

        self.connection_manager.save_connections() 
     
    def check_name(self, new_name, old_name):
        for c in self.connections:
            if new_name!= old_name and new_name == c["name"]:
                return True
            else:
                return False
            
    def get_active_connections(self):
        QApplication.processEvents()
        self.active_connections = set()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                env_name = item.text(1)
                self.active_connections.add(env_name)
        
        return self.active_connections

            
    
        
        
        
    