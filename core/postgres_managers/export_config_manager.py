from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

from core.data_models import (
    NewConfigPayload, UpdateConfigPayload,
    RemoveConfigPayload, UpdateConfigPresetListPayload
)

import logging
logger = logging.getLogger(__name__)

class PostgresExportConfigsManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_export_configs(self):
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        export_config_id,
                        export_config_name,
                        preset_id,
                        preset_name
                    FROM 
                        extraction.v_export_config_items
                """)
                data = cursor.fetchall()
                return data
                
        except Exception as e:
            logger.error("Failed to load export configs data from database.", exc_info=True)
            raise RuntimeError(f"Unable to load export configs data ({type(e).__name__}).")

        finally:
            self.db_manager.release_connection(conn)

    def add_export_config(self, new_config_payload: NewConfigPayload):
        conn = None
        try:
            conn = self.db_manager.get_connection()

            name = new_config_payload.name

            query = """
                INSERT INTO extraction.export_configs (name)
                VALUES (%(name)s)
                RETURNING row_id
            """

            params = {
                "name" : name
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                row_id = cursor.fetchone()[0]
                logger.info(f"{count} row/s inserted")

            conn.commit()
            return row_id

        except Exception as e:
            logger.error("Failed to remove add config to the database.", exc_info=True)
            raise RuntimeError(f"Unable to add export config from the data ({type(e).__name__}).")

        finally:
            self.db_manager.release_connection(conn)


    def update_export_config(self, update_config_payload: UpdateConfigPayload):
        conn = None
        try:
            conn = self.db_manager.get_connection()

            config_id = update_config_payload.id
            config_name = update_config_payload.new_name

            query = """
                UPDATE extraction.export_configs
                SET name = %(name)s
                WHERE row_id = %(id)s
            """

            params = {
                "name" : config_name,
                "id": config_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"{count} row/s updated")

            conn.commit()
            return True

        except Exception as e:
            logger.error("Failed to update export config in the database.", exc_info=True)
            raise RuntimeError(f"Unable to update export config in the database ({type(e).__name__}).")

        finally:
            self.db_manager.release_connection(conn)

    def remove_export_config(self, remove_config_payload: RemoveConfigPayload):
            conn = None
            try:
                conn = self.db_manager.get_connection()
    
                config_id = remove_config_payload.id
    
                query = """
                    DELETE FROM extraction.export_configs
                    WHERE row_id = %(id)s
                """
    
                params = {
                    "id": config_id
                }
    
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    count = cursor.rowcount
                    logger.info(f"{count} row/s removed")
    
                conn.commit()
                return True
    
            except Exception as e:
                logger.error("Failed to remove export config from the database.", exc_info=True)
                raise RuntimeError(f"Unable to remove export config from the database ({type(e).__name__}).")
    
            finally:
                self.db_manager.release_connection(conn)


    def update_config_preset_list(self, update_config_preset_list_payload: UpdateConfigPresetListPayload):

        conn = None
        err_msg = "Failed to perfrom any action."
        runtime_err_msg = "Unable to perform any action."
        query = ""
        params = {}
        
        try:
            conn = self.db_manager.get_connection()

            mode = update_config_preset_list_payload.mode
            config_id = update_config_preset_list_payload.config_id
            preset_id = update_config_preset_list_payload.preset_id

            if mode == "add":

                query = """
                    INSERT INTO extraction.export_config_items (export_config_id, preset_id)
                    VALUES (%(export_config_id)s, %(preset_id)s)
                """

                action = "inserted"
                err_msg = "Failed to insert preset item for the config in the database."
                runtime_err_msg = "Unable to insert preset item in the database."

            elif mode == "remove":

                query = """
                    DELETE FROM extraction.export_config_items
                    WHERE export_config_id = %(export_config_id)s and preset_id = %(preset_id)s
                """

                action = "removed"
                err_msg = "Failed to remove preset item for the config from the database."
                runtime_err_msg = "Unable to remove preset item from the database."

            params = {
                "export_config_id": config_id,
                "preset_id": preset_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"{count} row/s {action}")

            conn.commit()
            return True

        except Exception as e:
            logger.error(err_msg, exc_info=True)
            raise RuntimeError(f"{runtime_err_msg} ({type(e).__name__}).")

        finally:
            self.db_manager.release_connection(conn)
    
        
    
        
    

    

    
