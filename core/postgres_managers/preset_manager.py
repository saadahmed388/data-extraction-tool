from __future__ import annotations
from typing import TYPE_CHECKING
from core.data_models import (
    NewPresetPayload, UpdatePresetPayload, RemovePresetPayload,
    NewPresetItemPayload, UpdatePresetItemPayload, RemovePresetItemPayload
)

if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

import logging
logger = logging.getLogger(__name__)

class PostgresPresetsManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_presets(self):
        conn = None
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        preset_id,
                        preset_name,
                        env_id,
                        connection_name,
                        query_id,
                        query_name,
                        preset_item_id
                    FROM 
                        extraction.v_preset_items
                """)
                data = cursor.fetchall()
                return data
                
        except Exception as e:

            logger.error("Failed to load presets data due to an unexpected error.", exc_info=True)            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)


    def add_preset(self, new_preset_payload: NewPresetPayload) -> bool:
        conn = None
        row_id = None
        try:
            conn = self.db_manager.get_connection()
            query = """
                INSERT INTO extraction.presets (name)
                VALUES (%(name)s)
                RETURNING row_id
            """
            params = {
                "name": new_preset_payload.name
            }
            
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                row_id = cursor.fetchone()[0]
                logger.info(f"{count} rows/s inserted")
            
            conn.commit()
            return row_id
                
        except Exception as e:

            logger.error("Failed to add preset due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an insertion failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def remove_preset(self, remove_preset_payload: RemovePresetPayload) -> bool:

        conn = None

        try:

            preset_id = remove_preset_payload.id
            name = remove_preset_payload.name

            query = """
                DELETE FROM extraction.presets 
                WHERE row_id = %(preset_id)s
                RETURNING name
            """
            params = {
                "preset_id": preset_id
            }

            conn = self.db_manager.get_connection()
            
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                p_name = cursor.fetchone()[0]
                logger.info(f"{count} row/s deleted | Name : {p_name}")

            if count == 0:
                logger.warning(
                    "No preset found to be deleted | Name: %s",
                    name
                )
                return False
            
            conn.commit()
            return True            
        
        except Exception as e:

            logger.error("Failed to delete preset due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an deletion failure.", exc_info=rollback_err)
            
            raise e
        
        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def update_preset(self, update_preset_payload: UpdatePresetPayload) -> bool:
        conn = None

        try:

            preset_id = update_preset_payload.id
            old_name = update_preset_payload.old_name
            new_name = update_preset_payload.new_name

            conn = self.db_manager.get_connection()

            query = """
                UPDATE extraction.presets
                SET name = %(name)s
                WHERE row_id = %(preset_id)s
            """

            params = {
                "preset_id": preset_id,
                "name": new_name
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"Updated {count} row/s | Renamed preset {old_name} -> {new_name}")

            conn.commit()
            return True

        except Exception as e:

            logger.error("Failed to rename preset due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an update failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)


    def add_preset_item(self, new_preset_item_payload: NewPresetItemPayload):
        
        conn = None
        row_id = None
        
        try:

            conn = self.db_manager.get_connection()

            query = """
                INSERT INTO 
                    extraction.preset_items (preset_id, env_id, query_id)
                VALUES
                    (%(preset_id)s, %(con_id)s, %(query_id)s)
                RETURNING row_id
            """

            params = {
                "preset_id": new_preset_item_payload.preset_id,
                "con_id": new_preset_item_payload.con_id,
                "query_id": new_preset_item_payload.query_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                row_id = cursor.fetchone()[0]
                logger.info(f"Added {count} row/s | Preset: {new_preset_item_payload.preset_name}")

            conn.commit()
            return row_id

        except Exception as e:

            logger.error("Failed to add preset item to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an insertion failure.", exc_info=rollback_err)
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def update_preset_item(self, updated_preset_item_payload: UpdatePresetItemPayload):
        conn = None
        
        try:

            preset_name = updated_preset_item_payload.preset_name
            preset_item_id = updated_preset_item_payload.preset_item_id
            con_id = updated_preset_item_payload.con_id
            query_id = updated_preset_item_payload.query_id

            conn = self.db_manager.get_connection()

            query = """
                UPDATE 
                    extraction.preset_items pi
                SET 
                    env_id = %(con_id)s,
                    query_id = %(query_id)s
                WHERE
                    row_id = %(preset_item_id)s
            """

            params = {
                "preset_item_id": preset_item_id,
                "con_id": con_id,
                "query_id": query_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"Updated {count} item/s | preset: {preset_name}")
            conn.commit()
            return True

        except Exception as e:

            logger.error("Failed to update preset item to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an update failure.", exc_info=rollback_err)            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def remove_preset_item(self, remove_preset_item_payload: RemovePresetItemPayload):
        
        conn = None
        
        try:

            preset_item_id = remove_preset_item_payload.preset_item_id
            preset_name = remove_preset_item_payload.preset_name

            conn = self.db_manager.get_connection()

            query = """
                DELETE FROM extraction.preset_items
                WHERE row_id = %(preset_item_id)s                
            """

            params = {
                "preset_item_id": preset_item_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"Deleted {count} item/s | Preset: {preset_name}")

            conn.commit()
            return True

        except Exception as e:

            logger.error("Failed to delete preset item to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling a deletion failure.", exc_info=rollback_err)            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)




        
            

