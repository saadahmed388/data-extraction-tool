<<<<<<< HEAD
from PyQt5.QtCore import QObject, pyqtSignal

import json
import os
=======
from __future__ import annotations
from PyQt5.QtCore import QObject, pyqtSignal
from collections import defaultdict
from typing import TYPE_CHECKING

from core.data_models import (
    NewConfigPayload, RemoveConfigPayload, 
    UpdateConfigPayload, UpdateConfigPresetListPayload
)
from core.exceptions import InsertionError, InvalidOperation

import json
import os
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.postgres_managers.export_config_manager import PostgresExportConfigsManager
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)

class ExportConfigManager(QObject):
    
    export_configs_updated = pyqtSignal()
    
    def __init__(self, postgres_export_config_manager: PostgresExportConfigsManager):
        super().__init__()

        self.postgres_export_config_manager = postgres_export_config_manager
        configs_data = self.postgres_export_config_manager.load_export_configs()
        self.export_configs = ExportConfigManager.group_data(configs_data)
    
    @staticmethod
    def group_data(data):
        configs = {}
        if data is not None:
            for d in data:

                config_id = d[0]
                config_name = d[1]
                preset_id = d[2]
                preset_name = d[3]

                if config_id not in configs.keys():
                    configs[config_id] = {
                        "name": config_name,
                        "presets": {},
                        "last_extracted": None
                    }
                configs[config_id]["presets"][preset_id] = preset_name
            return configs

    @property
    def all_configs(self):
        return self.export_configs

    @property
    def config_name_id_map(self):
        return {v["name"]: k for k, v in self.export_configs.items()}

    @property
    def config_names(self):
        return {v["name"] for v in self.export_configs.values()}

    def get_config_id(self, config_name):
        return self.config_name_id_map[config_name]
        
    def new_export_config(self, new_export_config_payload: NewConfigPayload):
        
        try:

            name = new_export_config_payload.name

            export_config_id = self.postgres_export_config_manager.add_export_config(new_export_config_payload)

            
            if not export_config_id:
                raise InsertionError(f"Failed to add Query: {name}")
            
            new_entry = {
                "name" : name,
                "presets" : {},
                "last_extracted": None                    
            }

            self.export_configs[export_config_id] = new_entry
            self.export_configs_updated.emit()

        except Exception as e:

            logger.error(f"Failed to add export config {name} at the database layer", exc_info=True)
            raise RuntimeError(f"Unable to add preset ({type(e).__name__}: {e}).") from e 
    
    
    def remove_export_config(self, remove_export_config_payload: RemoveConfigPayload):
        
        try:
        
            export_config_id = remove_export_config_payload.id
            export_config_name = remove_export_config_payload.name

            self.postgres_export_config_manager.remove_export_config(remove_export_config_payload)
            self.export_configs.pop(export_config_id, None)

            self.export_configs_updated.emit()
            return True

        except Exception as e:

            logger.error(f"Failed to remove preset {export_config_name} at the application layer", exc_info=True)
            raise RuntimeError(f"unable to remove preset ({type(e).__name__}: {e}).") from e 


            
    def update_export_config(self, update_export_config_payload: UpdateConfigPayload):
        
        try:
        
            export_config_id = update_export_config_payload.id
            export_config_old_name = update_export_config_payload.old_name
            export_config_new_name = update_export_config_payload.new_name

            self.postgres_export_config_manager.update_export_config(update_export_config_payload)
            self.export_configs[export_config_id]["name"] = export_config_new_name

            self.export_configs_updated.emit()
            return True

        except Exception as e:

            logger.error(f"Failed to update export config {export_config_old_name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to remove preset ({type(e).__name__}: {e}).") from e 

    def update_config_preset_list(self, update_config_preset_list_payload: UpdateConfigPresetListPayload):

        try:

            config_id = update_config_preset_list_payload.config_id
            preset_list = update_config_preset_list_payload.preset_list
            preset_id = update_config_preset_list_payload.preset_id
            preset_name = update_config_preset_list_payload.preset_name
            mode = update_config_preset_list_payload.mode

            if mode not in ['add', 'remove']:
                raise InvalidOperation("Operation not valid. Operation can be either 'add' or 'remove'.")

            self.postgres_export_config_manager.update_config_preset_list(update_config_preset_list_payload)

            if mode == "add":
                self.export_configs[config_id]["presets"][preset_id] = preset_name
            if mode == "remove":
                self.export_configs[config_id]["presets"].pop(preset_id, None)

            self.export_configs_updated.emit()
            return True

        except Exception as e: 

            logger.error(f"Failed to {mode} preset item at the application layer", exc_info=True)
            raise RuntimeError(f"Failed to {mode} preset item ({type(e).__name__}: {e}).") from e 

    
        
        
    
        
            
        
        
