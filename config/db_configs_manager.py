class DBConfigsManager:
    def __init__(self, filepath = "configs/connections.json"):
        self.filepath = filepath
        self.connections = {}
               
    def load_connections(self):
        with open(filepath, r) as f:
            self.connections = json.load(f)
        return self.connections
    
    def add_connection(self, env, username, password, dns):
        new_connection = {
                            "user" : username,
                            "password" : password,
                            "dns" : dns
                          }
        self.connections[env] = new_connection
        self.save_connections()
    
    def save_connection(self):
        with open(filepath, w) as f:
            json.dump(self.connections, f)
        
        
        
        
        