import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class PresetManager(QObject):
    presets_updated = pyqtSignal()
    presets_list_updated = pyqtSignal()
    def __init__(self, filepath = "data_and_config_files/presets.json"):
        super().__init__()
        folder = os.path.dirname(filepath)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        self.filepath = filepath   
        self.presets = {}
        self.load_presets()
        
        
    def new_preset(self, preset_name):
        
        new_preset = [

                        { "active" : True, "env" : "Okayama",   "sql" : "None"},
                        { "active" : True, "env" : "Aomori",    "sql" : "None"},
                        { "active" : True, "env" : "Hakodate",  "sql" : "None"},
                        { "active" : True, "env" : "Iwate",     "sql" : "None"},
                        { "active" : True, "env" : "Shikoku",   "sql" : "None"},
                        { "active" : True, "env" : "Okinawa",   "sql" : "None"},
                        { "active" : True, "env" : "Wakayama",   "sql" : "None"},
                        { "active" : True, "env" : "Chugoku",   "sql" : "None"}
                     
                     ]
                     
        self.presets[preset_name] = new_preset
        self.save_preset()
    
    def load_presets(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if not content:
                    self.presets = {}       # or default presets
                else:
                    self.presets = json.loads(content)
        else:
            self.presets = {}
        
        
    def save_preset(self):
        with open(self.filepath, "w") as f:
            json.dump(self.presets, f, indent = 4)
        self.presets_updated.emit()
    
    def remove_preset(self, env):
        if env in self.presets.keys():
            del self.presets[env]
        self.save_preset()
        self.presets_list_updated.emit()
        
    def get_all_presets(self):
        return self.presets
        