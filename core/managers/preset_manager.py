<<<<<<< HEAD
from PyQt5.QtCore import QObject, pyqtSignal

import json
import os
=======
from __future__ import annotations
from typing import TYPE_CHECKING
from PyQt5.QtCore import QObject, pyqtSignal
from collections import defaultdict

from core.data_models import (
    NewPresetPayload, UpdatePresetPayload, RemovePresetPayload,
    NewPresetItemPayload, UpdatePresetItemPayload, RemovePresetItemPayload
)

from core.exceptions import NotFound, InsertionError

import logging
import json
import os

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.postgres_managers.preset_manager import PostgresPresetsManager
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)

class PresetManager(QObject):

    preset_updated = pyqtSignal(str)
    presets_list_updated = pyqtSignal()
    
    def __init__(self, postgres_preset_manager: PostgresPresetsManager):
        
        super().__init__() 

        self.postgres_preset_manager = postgres_preset_manager
        preset_data = self.postgres_preset_manager.load_presets() 
        self.presets = PresetManager.group_data(preset_data)
    

    @staticmethod
    def group_data(data: list):

        presets = defaultdict(dict)
        
        for d in data:

            presets.setdefault(d[0], {"name": d[1], "items": {}})

            if d[6] is not None:
                presets[d[0]]["items"][d[6]] = {"env": d[3], "sql": d[5]}

        return presets   


    @property
    def all_presets(self):
        return self.presets

    @property
    def preset_list(self):
        return {v["name"]: k for k, v in self.presets.items()}

    @property
    def preset_name_id_map(self):
        return {v["name"]: k for k, v in self.presets.items()}

    def add_preset(self, new_preset_payload: NewPresetPayload) -> bool:
        try:

            preset_name = new_preset_payload.name
            preset_id = self.postgres_preset_manager.add_preset(new_preset_payload)            
            
            self.presets[preset_id] = {
                "name": preset_name,
                "items": {}
            }
            
            self.presets_list_updated.emit()

            return True

        except Exception as e:
            
            logger.error(f"Failed to add preset {preset_name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to add preset ({type(e).__name__}: {e}).") from e 

    def remove_preset(self, remove_preset_payload: RemovePresetPayload) -> bool:

        try:

            id = remove_preset_payload.id
            name = remove_preset_payload.name

            self.postgres_preset_manager.remove_preset(remove_preset_payload)
            self.presets.pop(id, None)
            self.presets_list_updated.emit()
            
            return True
        
        except Exception as e:

            logger.error(f"Failed to remove preset {name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to remove preset ({type(e).__name__}: {e}).") from e 

    def update_preset(self, update_preset_payload: UpdatePresetPayload) -> bool:

        try:

            id = update_preset_payload.id
            old_name = update_preset_payload.old_name
            new_name = update_preset_payload.new_name

            self.postgres_preset_manager.update_preset(update_preset_payload)
            self.presets[id]["name"] = new_name
            self.presets_list_updated.emit()

            return True
        
        except Exception as e:

            logger.error(f"Failed to update preset {old_name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update preset ({type(e).__name__}: {e}).") from e 

    def add_preset_item(self, new_preset_item_payload: NewPresetItemPayload):
        
        try:

            preset_id = new_preset_item_payload.preset_id

            preset_name = new_preset_item_payload.preset_name
            con_name = new_preset_item_payload.con_name
            query_name = new_preset_item_payload.query_name
            

            preset_item_id = self.postgres_preset_manager.add_preset_item(new_preset_item_payload)
            
            if not preset_item_id:
                raise InsertionError(f"Failed to add Query: {query_name} on Connection: {con_name} for preset {preset_name}")

            self.presets[preset_id]["items"][preset_item_id] = {
                "env": con_name,
                "sql": query_name
            }
            
            self.preset_updated.emit(preset_id)
            return True
        
        except Exception as e:

            logger.error(f"Failed to add preset item at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to add preset item ({type(e).__name__}: {e}).") from e 

    def remove_preset_item(self, remove_preset_item_payload: RemovePresetItemPayload):

        try:

            preset_item_id = remove_preset_item_payload.preset_item_id
            preset_id = remove_preset_item_payload.preset_id

            self.postgres_preset_manager.remove_preset_item(remove_preset_item_payload)
            self.presets[preset_id]["items"].pop(preset_item_id, None)
            self.preset_updated.emit(preset_id)

            return True
        
        except Exception as e:

            logger.error(f"Failed to remove preset item at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to remove preset item ({type(e).__name__}: {e}).") from e 

    def update_preset_item(self, update_preset_item_payload: UpdatePresetItemPayload):

        try:

            preset_item_id = update_preset_item_payload.preset_item_id
            preset_id = update_preset_item_payload.preset_id

            con_name = update_preset_item_payload.con_name
            query_name = update_preset_item_payload.query_name
            
            self.postgres_preset_manager.update_preset_item(update_preset_item_payload)
            
            self.presets[preset_id]["items"][preset_item_id]["env"] = con_name
            self.presets[preset_id]["items"][preset_item_id]["sql"] = query_name

            self.preset_updated.emit(preset_id)

            return True
        
        except Exception as e:
            
            logger.error(f"Failed to update preset item at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update preset item ({type(e).__name__}: {e}).") from e 
