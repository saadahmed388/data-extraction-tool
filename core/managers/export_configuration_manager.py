import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class ExportConfigManager(QObject):
    export_configs_updated = pyqtSignal()
    def __init__(self, filepath = 'data_and_config_files/export_configs.json'):
        super().__init__()
        self.filepath = filepath
        folder = os.path.dirname(self.filepath)
        if not os.path.exists(folder):
           os.mkdirs(folder, exists_ok = True)
        self.export_configs = {}
        self.load_export_configs()
        
    def load_export_configs(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if not content:
                    self.export_configs = {}
                else:
                    self.export_configs = json.loads(content)
        else:
            self.export_configs = {}

    def new_export_config(self, name):
        new_entry = {
                        "preset_list" : []                        
                    }
        self.export_configs[name] = new_entry
        self.save_export_configs()
        
    def save_export_configs(self):
        with open(self.filepath, "w") as f:
            json.dump(self.export_configs, f, indent = 4)
        self.export_configs_updated.emit()
    
    def delete_export_config(self, name):
        del self.export_configs[name]
        self.save_export_configs()
    
    def rename_config(self, new_name, old_name):
        self.export_configs = self.renaming_helper(new_name, old_name)
        self.save_export_configs()
    
    def get_all_configs(self):
        return self.export_configs
        
    def renaming_helper(self, new_name, old_name):
        new_dict = {}
        
        for k, v in self.export_configs.items():
            if k == old_name:
                new_dict[new_name] = v
            else:
                new_dict[k] = v
        
        return new_dict
    
        
        
    
        
            
        
        
