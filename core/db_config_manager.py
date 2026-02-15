import json
import os
from PyQt5.QtCore import QObject, pyqtSignal

class DBConfigManager(QObject):
    connections_updated = pyqtSignal()
    def __init__(self, filepath = "data_and_config_files/connections.json"):
        super().__init__()
        folder = os.path.dirname(filepath)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        self.filepath = filepath   
        self.connections = []
        self.load_connections()
               
    def get_all_connections(self):
        return self.connections
               
    def load_connections(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.connections = json.load(f)
            except Exception:
                self.connections = []
        else:
            self.connections = []
    
    def add_connection(self, name, username, password, dsn):
        self.new_connection =   {   
                                    "name" : name,
                                    "user" : username,
                                    "password" : password,
                                    "dsn" : dsn
                                }
        self.connections.append(self.new_connection)                         
        self.save_connections()
    
    def save_connections(self):
        with open(self.filepath, "w") as f:
            json.dump(self.connections, f, indent=4)
        self.connections_updated.emit()   
    
    def remove_connection(self, name):
        self.connections = [con for con in self.connections if con["name"]!=name]
        self.save_connections()
    
    
        
        
        
        
        
        