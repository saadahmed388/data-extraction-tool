from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

from core.data_models import (
    NewSRPayload, UpdateSRPayload, 
    RemoveSRPayload, UpdateSRConfigPayload
)

import logging
logger = logging.getLogger(__name__)

class PostgresExportManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_exports(self):
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        sr_id,
                        sr_num,
                        config_id,
                        config_name
                    FROM 
                        extraction.v_sr_view
                """)
                data = cursor.fetchall()
                return data
                
        except Exception:
            logger.exception("Failed to load Export SRs from database.")

        finally:
            self.db_manager.release_connection(conn)


    def create_new_sr(self, new_sr_payload: NewSRPayload):

        conn = None
        row_id = None
        
        try:
            conn = self.db_manager.get_connection()
            query = """
                INSERT INTO extraction.extraction_run (sr_num, export_config_id)
                VALUES (%(sr_num)s, %(export_config_id)s)
                RETURNING row_id
            """
            params = {
                "sr_num" : new_sr_payload.sr_num,
                "export_config_id": new_sr_payload.export_config_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                row_id = cursor.fetchone()[0]
                logger.info(f"{count} rows/s inserted")
            
            conn.commit()
            return row_id
                
        except Exception as e:
            
            logger.error("Failed to insert record into the database due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an insertion failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)


    def remove_sr(self, remove_sr_payload: RemoveSRPayload):
        
        conn = None
        
        try:
        
            conn = self.db_manager.get_connection()
            query = """
                DELETE FROM extraction.extraction_run
                WHERE row_id = %(sr_id)s
            """
            params = {
                "sr_id" : remove_sr_payload.sr_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"{count} rows/s removed")
            
            conn.commit()
            return True
                
        except Exception as e:
            
            logger.error("Failed to remove record from the database due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling a deletion failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)
    
    def update_sr(self, update_sr_payload: UpdateSRPayload):
        
        conn = None
        
        try:
        
            conn = self.db_manager.get_connection()
            query = """
                UPDATE extraction.extraction_run
                SET sr_num = %(sr_num)s
                WHERE row_id = %(sr_id)s
            """
            params = {
                "sr_id" : update_sr_payload.sr_id,
                "sr_num": update_sr_payload.new_sr_num
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"{count} rows/s updated")
            
            conn.commit()
            return True
                
        except Exception as e:
            
            logger.error("Failed to update record in the database due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an update failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def update_sr_config(self, update_sr_config_payload: UpdateSRConfigPayload):

        conn = None
                
        try:
        
            conn = self.db_manager.get_connection()
            query = """
                UPDATE extraction.extraction_run
                SET export_config_id = %(export_config_id)s
                WHERE row_id = %(sr_id)s
            """
            params = {
                "sr_id" : update_sr_config_payload.sr_id,
                "export_config_id": update_sr_config_payload.export_config_id
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                logger.info(f"{count} rows/s updated")
            
            conn.commit()
            return True
                
        except Exception as e:
            
            logger.error("Failed to update record in the database due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an update failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager





