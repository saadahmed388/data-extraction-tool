from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
from utilities.custom_widgets import StyledInputDialog
from PyQt5.QtCore import Qt
from core.db_client import DBClient

class ConnectionsTab(QWidget):
    def __init__(self, db_clients, db_configs_manager, styling_manager):
        super().__init__()
        self.db_configs_manager = db_configs_manager
        self.styling_manager = styling_manager
        self.connections = []
        self.db_clients = db_clients
                
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
        self.db_configs_manager.connections_updated.connect(self.load_connections)
        self.load_connections()
        
    def load_connections(self):
        self.tree.clear()
        self.connections = self.db_configs_manager.get_all_connections()
        self.connect_all()
        for connection in self.connections:
            env = connection["name"]
            user = connection["user"]
            dsn = connection["dsn"]
            item = QTreeWidgetItem(['', env, user, dsn])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setTextAlignment(0, Qt.AlignCenter)
            item.setCheckState(0, Qt.Checked)
            self.tree.addTopLevelItem(item)
            
    def add_connection(self):
        
        name, ok1 = StyledInputDialog("Add Connection", "Enter connection name:").get_text()        
        if not ok1 or not name:
            return
        username, ok2 = StyledInputDialog("Username", "Enter Username:", "Y").get_text()
        if not ok2 or not username:
            return   
        password, ok3 = StyledInputDialog("Password", "Enter Password:", "Y").get_text()
        if not ok3 or not password:
            return            
        dsn, ok4 = StyledInputDialog("DSN", "Enter DSN:", "Y").get_text()
        if not ok4 or not dsn:
            return 
        
        self.db_configs_manager.add_connection(name, username, password, dsn)
    
    def remove_connection(self):
        
        self.db_configs_manager.remove_connection(self.tree.currentItem().text(0))
    
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
        
        new_username, ok2 = StyledInputDialog("Edit Username", "Enter new username:", "Y", old_username).get_text()
        if not ok2 or not new_username:
            return
            
        new_password, ok3 = StyledInputDialog("Edit Password", "Enter new password:", "Y", old_password).get_text()
        if not ok3 or not new_password:
            return
            
        new_dsn, ok4 = StyledInputDialog("Edit DSN", "Enter new DSN:", "Y", old_dsn).get_text()
        if not ok4 or not new_dsn:
            return
        
        for c in self.connections:
            if c["name"] == old_name:
                if ok1 and new_name.strip():
                    c["name"] = new_name.strip()
                if ok2 and new_username.strip():
                    c["user"] = new_username.strip()
                if ok3 and new_password.strip():
                    c["password"] = new_password.strip()
                if ok4 and new_dsn.strip():
                    c["dsn"] = new_dsn.strip()
                break

        self.db_configs_manager.save_connections() 
     
    def check_name(self, new_name, old_name):
        for c in self.connections:
            if new_name!= old_name and new_name == c["name"]:
                return True
            else:
                return False
    
    def connect_all(self):
        
        for c in self.connections:
            con_name = c["name"]
            connection = DBClient(
                user=c["user"],
                password=c["password"],
                dsn=c["dsn"]
            )
            try:
                connection.connect()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    f"{con_name} connection failed:\n{str(e)}"
                )
            
            self.db_clients[con_name] = connection
            
    def get_active_connections(self):
        QApplication.processEvents()
        self.active_connections = set()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                env_name = item.text(1)
                self.active_connections.add(env_name)
        
        return self.active_connections

            
    
        
        
        
    