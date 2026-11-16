from __future__ import annotations

from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.models.data_models import ReportPayload
from core.exceptions.exceptions import InsertionError, InvalidInputError

import logging
import json
import os

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.postgres_managers.history_manager import PostgresHistoryManager

class HistoryManager(QObject):
    history_updated = pyqtSignal()
    def __init__(
            self, 
            postgres_history_manager: PostgresHistoryManager
        ):

        super().__init__()
        
        self.postgres_history_manager = postgres_history_manager
        history_data = self.postgres_history_manager.load_history()
        self.history = HistoryManager.group_data(history_data)
    
    @property
    def all_history(self):
        return self.history

    @staticmethod
    def group_data(data):

        history = {}

        for d in data:

            history_id = d[0]
            sr_num = d[1]
            config_name = d[2]

            report = d[4]

            if not d[5]: 
                date_extracted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_extracted = d[5].strftime('%Y-%m-%d %H:%M:%S')
                
            start_time = d[6]
            end_time = d[7]

            history[history_id] = {
                "sr_num": sr_num,
                "config": config_name,
                "date_extracted": date_extracted,
                "extraction_log": report["logs"],
                "runtime_duration": HistoryManager.calc_runtime(start_time, end_time)
            }

        return history

    @staticmethod
    def calc_runtime(start_time, end_time):

        start_time = start_time or datetime.now()
        end_time = end_time or datetime.now()

        elapsed_seconds = (end_time - start_time).total_seconds()
        minutes, seconds = divmod(int(elapsed_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"
        
      
    def load_history(self):
        history = []
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        return history

    def add_report(self, add_history_payload: ReportPayload):
        
        try:

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            sr_id = add_history_payload.sr_id
            sr_num = add_history_payload.sr_num
            config_id = add_history_payload.config_id
            config_name = add_history_payload.config_name
            status = add_history_payload.status
            start_time = add_history_payload.start_time
            end_time = add_history_payload.end_time
            report = add_history_payload.report

            # add_history_payload.start_time = datetime.fromtimestamp(start_time, tz=timezone.utc)
            # add_history_payload.end_time = datetime.fromtimestamp(end_time, tz=timezone.utc)
            add_history_payload.report = json.dumps(add_history_payload.report)

            history_id = self.postgres_history_manager.add_history_record(add_history_payload)   

            if not history_id:
                raise InsertionError(f"Failed to add record as history for sr_num: {sr_num} and config: {config_name} at {timestamp}")

            history_item = {
                "sr_num": sr_num,
                "config": config_name,
                "date_extracted": timestamp,
                "extraction_log": report["logs"],
                "runtime_duration": HistoryManager.calc_runtime(start_time, end_time)
            }

            self.history = {history_id : history_item, **self.history}

            self.history_updated.emit()

            return True

        except Exception as e:

            logger.error(f"Failed to add history at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to add history item ({type(e).__name__}: {e}).") from e


    def get_last_extracted(self, entity_type: str, entity_id: str):       
    
        try:

            if not entity_type or not entity_type:
                raise InvalidInputError("Input cannot be empty. Entity Type or Entity ID is Empty.")

            if entity_type not in ("sr_num", "config"):
                raise InvalidInputError(f"Unsupported entity_type: {entity_type}")

            history = self.history

            latest_date = None
            
            match entity_type:
                
                case "sr_num":
                    latest_date = next(
                        (
                            hist["date_extracted"]
                            for hist in history.values() if hist["sr_num"] == entity_id
                        ),
                        None,
                    )
                
                case "config":
                    latest_date = next(
                        (
                            hist["date_extracted"]
                            for hist in history.values() if hist["config"] == entity_id
                        ),
                        None, 
                    )
            
            return latest_date or "No Extractions yet"

        except Exception as e:

            logger.error(f"Failed to retrieve the last extracted date at the app layer", exc_info=True)
            raise RuntimeError(f"Unable to fetch the last extracted date ({type(e).__name__}: {e}).") from e


    def get_logs(self, entity_type: str, entity_id: str): 

        try:
        
            if not entity_type or not entity_type:
                raise InvalidInputError("Input cannot be empty. Entity Type or Entity ID is Empty.")

            if entity_type not in ("sr_num", "config"):
                raise InvalidInputError(f"Unsupported entity_type: {entity_type}")

            history = self.history
            logs = []
            
            match entity_type:
                
                case "sr_num":
                    logs = [
                        hist["extraction_log"]
                        for hist in history.values() if hist["sr_num"] == entity_id
                    ]
                
                case "config":
                    logs = [
                        hist["extraction_log"]
                        for hist in history.values() if hist["config"] == entity_id
                    ]

            return logs

        except Exception as e:

            logger.error(f"Failed to retrieve logs at the app layer", exc_info=True)
            raise RuntimeError(f"Unable to fetch logs ({type(e).__name__}: {e}).") from e