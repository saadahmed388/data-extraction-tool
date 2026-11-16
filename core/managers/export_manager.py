from __future__ import annotations
from PyQt5.QtCore import QObject, pyqtSignal
from typing import TYPE_CHECKING

from core.models.data_models import (
    NewSRPayload, UpdateSRPayload, 
    RemoveSRPayload, UpdateSRConfigPayload
)

from core.exceptions.exceptions import InsertionError, UpdateError

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.postgres_managers.export_manager import PostgresExportManager

class ExportManager(QObject):
    sr_config_updated = pyqtSignal()
    def __init__(self, postgres_export_manager: PostgresExportManager):
        super().__init__()

        self.postgres_export_manager = postgres_export_manager
        sr_configs = self.postgres_export_manager.load_exports()
        self.sr_configs = self.group_data(sr_configs)        
        
    @staticmethod
    def group_data(data):

        exports = {}

        for d in data:

            sr_id = d[0]
            sr_num = d[1]
            config_id = d[2]
            config_name = d[3]

            exports[sr_id] = {
                "sr_num": sr_num,
                "config_id": config_id,
                "config_name": config_name
            }

        return exports

    @property
    def all_sr_configs(self):
        return self.sr_configs

    @property
    def sr_num_id_map(self):
        return {v["sr_num"]: k for k, v in self.sr_configs.items()}

    @property
    def sr_nums(self):
        return {v["sr_num"] for v in self.sr_configs.values()}
    
    def new_export_sr(self, new_sr_payload: NewSRPayload):

        try:

            sr_id = self.postgres_export_manager.create_new_sr(new_sr_payload)

            if not sr_id:
                raise InsertionError(f"Failed to add sr: {sr_num}")

            sr_num = new_sr_payload.sr_num
            config_id = new_sr_payload.export_config_id
            config_name = new_sr_payload.export_config_name

            self.sr_configs[sr_id] = {
                "sr_num": sr_num,
                "config_id": config_id,
                "config_name" : config_name
            }
            
            self.sr_config_updated.emit()

            return True

        except Exception as e:
            
            logger.error(f"Failed to update preset item at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update preset item ({type(e).__name__}: {e}).") from e

    def update_export_sr(self, update_sr_payload: UpdateSRPayload):

        try:

            sr_id = update_sr_payload.sr_id
            old_sr_num = update_sr_payload.old_sr_num
            new_sr_num = update_sr_payload.new_sr_num
            
            self.postgres_export_manager.update_sr(update_sr_payload)

            export_detail = self.sr_configs.get(sr_id, None)
            
            if export_detail is None:
                raise UpdateError("SR ID does not exist in cache!")

            export_detail["sr_num"] = new_sr_num
            self.sr_configs[sr_id] = export_detail
            
            self.sr_config_updated.emit()

            return True

        except Exception as e:
            
            logger.error(f"Failed to update SR# {old_sr_num} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update sr ({type(e).__name__}: {e}).") from e

    def remove_sr(self, remove_sr_payload: RemoveSRPayload):

        try:
        
            sr_id = remove_sr_payload.sr_id
            sr_num = remove_sr_payload.sr_num
            
            self.postgres_export_manager.remove_sr(remove_sr_payload)

            self.sr_configs.pop(sr_id, None)
            self.sr_config_updated.emit()

            return True

        except Exception as e:
            
            logger.error(f"Failed to remove SR# {sr_num} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update sr ({type(e).__name__}: {e}).") from e

    def update_export_sr_config(self, update_sr_config_payload: UpdateSRConfigPayload):

        try:

            sr_id = update_sr_config_payload.sr_id
            export_config_id = update_sr_config_payload.export_config_id
            export_config_name = update_sr_config_payload.export_config_name

            self.postgres_export_manager.update_sr_config(update_sr_config_payload)

            self.sr_configs[sr_id]["config_id"] = export_config_id
            self.sr_configs[sr_id]["config_name"] = export_config_name

            self.sr_config_updated.emit()
 
        except Exception as e:
            
            logger.error(f"Failed to update export config at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update export config ({type(e).__name__}: {e}).") from e

