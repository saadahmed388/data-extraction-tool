import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
import uuid

class ExportManager(QObject):
    exports_updated = pyqtSignal()
    def __init__(self, filepath = 'data_and_config_files/exports.json'):
        super().__init__()
        folder = os.path.dirname(filepath)
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.filepath = filepath
        self.exports = {}
        self.load_exports()
        
    def load_exports(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if content:
                    self.exports = json.loads(content)
                else:
                    self.exports = {}
        else:
            self.exports = {}           
    
    def new_export(self, name):
        self.exports[name] = {
                                "config_name" : "",
                                "extracted_on" : "No Extractions Yet",
                                "extraction_log" : ""
                             }
        self.save_exports()
    
    def save_exports(self):
        with open(self.filepath, "w") as f:
            json.dump(self.exports, f, indent = 4)
        self.exports_updated.emit()
    
    def get_all_exports(self):
        return self.exports
    
    def remove_export(self, name):
        del self.exports[name]
        self.save_exports()