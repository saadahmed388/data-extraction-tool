<<<<<<< HEAD
=======
from __future__ import annotations

>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
from typing import TYPE_CHECKING

import json
import os

if TYPE_CHECKING:
    from core.postgres_managers.history_manager import PostgresHistoryManager

import json
import os

class HistoryManager(QObject):
    history_updated = pyqtSignal()
    def __init__(
            self, 
            postgres_history_manager: PostgresHistoryManager,
            filepath = "data_and_config_files/history.json"
        ):
        super().__init__()
        folder = os.path.dirname(filepath)
        os.makedirs(folder, exist_ok=True)
        self.filepath = filepath   
        
        self.postgres_history_manager = postgres_history_manager
        history_data = self.postgres_history_manager.load_history()
        self.history = self.group_data(history_data)
        # self.load_history()

    @staticmethod
    def group_data(data):
        history_list = []
        for d in data:
            history_list.append({
                "sr_num": d[1],
                "config": d[2],
                "date_extracted": d[5],
                "extraction_log": d[4]
            })

        return history_list
      
    def load_history(self):
        history = []
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        return history

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