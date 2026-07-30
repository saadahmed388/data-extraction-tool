import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from core.db_client import DBClient
import logging

logger = logging.getLogger(__name__)

class ConnectionManager(QObject):
    connections_updated = pyqtSignal()
    def __init__(self, filepath = "data_and_config_files/connections.json"):
        super().__init__()
        folder = os.path.dirname(filepath)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        self.filepath = filepath   
        self.connections = self.load_connections()
        self.db_clients = {}
        self.connect_all()
               
    def get_all_connections(self):
        return self.connections

    def get_all_clients(self):
        return self.db_clients
               
    def load_connections(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read()
                if content:
                    return json.loads(content)
            return []
    
    def add_connection(self, name, username, password, dsn):
        self.new_connection = {
                            "name" : name,
                            "user" : username,
                            "password" : password,
                            "dsn" : dsn
                          }

        connection = DBClient(
            user=username,
            password=password,
            dsn=dsn
        )

        pool = connection.pool
        if self.test_pool(pool, name):                     
            self.connections.append(self.new_connection)                         
            self.db_clients[name] = connection
            self.save_connections()
            return True

        del connection
        return False

    def save_connections(self):
        with open(self.filepath, "w") as f:
            json.dump(self.connections, f, indent=4)
        self.connections_updated.emit()   
    
    def remove_connection(self, name):
        self.connections = [con for con in self.connections if con["name"]!=name]
        del self.db_clients[name] 
        self.save_connections()

    def connect_modified(self, env, username, password, dsn, db_clients):    
        connection = DBClient(
            user=username,
            password=password,
            dsn=dsn
        )
        pool = connection.pool
        if self.test_pool(pool, env):            
            db_clients[env] = connection    
            return True
        return False

    def connect_all(self):
        for c in self.connections:
            con_name = c["name"]
            connection = DBClient(
                user=c["user"],
                password=c["password"],
                dsn=c["dsn"]
            )
            
            pool = connection.pool
            if self.test_pool(pool, con_name):            
                self.db_clients[con_name] = connection 
        
    def test_pool(self, pool, env):
        try:
            with pool.acquire() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM dual")
            logger.info(f"{env} pool OK")
            print("pass")
            return True
        
        except Exception as e:
            logger.exception(f"{env} pool FAILED: {e}")
            print("fail")
            return False


    
    
        
        
        
        
        
        