import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime 

class QueryManager(QObject):
    queries_updated = pyqtSignal()
    def __init__(self, filepath="data_and_config_files/queries.json"):
        super().__init__()
        folder = os.path.dirname(filepath)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        self.filepath = filepath
        self.queries = []
        self.load_queries()

    def load_queries(self):
        """Load queries from JSON file into memory."""
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.queries = json.load(f)
        else:
            self.queries = []

    def save_queries(self):
        """Write current queries list to JSON file."""
        with open(self.filepath, "w") as f:
            json.dump(self.queries, f, indent=4)
        self.queries_updated.emit()

    def add_query(self, name, sql):
        """Add new query and save."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.queries.append({
                                "name": name, 
                                "sql": sql, 
                                "date_added_on": timestamp,
                                "date_modified_on": timestamp
                            })
        self.save_queries()
    
    def delete_query(self, name):
        """Delete query by name and save."""
        self.queries = [q for q in self.queries if q["name"] != name]
        self.save_queries()

    def get_all_queries(self):
        """Return all queries (safe getter)."""
        return self.queries
