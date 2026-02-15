import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class HistoryManager(QObject):
    history_updated = pyqtSignal()
    def __init__(self, filepath = "data_and_config_files/history.json"):
        super().__init__()
        folder = os.path.dirname(filepath)
        os.makedirs(folder, exist_ok=True)
        self.filepath = filepath   
        self.history = []
        self.load_history()
      
    def load_history(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if not content:
                    self.history = []
                else:
                    self.history = json.loads(content)
        else:
            self.history = []

    def add_history(self, sr_num, config, log):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = {
                    "sr_num" : sr_num,
                    "config" : config,
                    "date_extracted" : timestamp,
                    "extraction_log" : log
                }                
        
        self.history.append(entry)
        self.save_history()        
    
    def save_history(self):
        with open(self.filepath, "w") as f:
            json.dump(self.history, f, indent = 4)
        self.history_updated.emit()
    
    def get_all_history(self):
        return self.history