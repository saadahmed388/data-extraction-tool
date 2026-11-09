from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

import logging
logger = logging.getLogger(__name__)

class PostgresHistoryManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_history(self):
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        errep.row_id,
                        er.sr_num,
                        ec.name,
                        errep.status,
                        errep.report,
                        to_char(errep.created, 'DD-MM-YYYY HH24:MI:SS') AS created,
                        to_char(errep.run_start_time, 'DD-MM-YYYY HH24:MI:SS') AS run_start_time,
                        to_char(errep.run_end_time, 'DD-MM-YYYY HH24:MI:SS') AS run_end_time
                    FROM 
                        extraction.extraction_run_report errep
                        JOIN extraction.extraction_run er ON errep.extn_run_id = er.row_id
                        JOIN extraction.export_configs ec ON er.export_config_id = ec.row_id
                        ORDER BY created DESC, sr_num DESC
                """)
                data = cursor.fetchall()
                return data
                
        except Exception:
            logger.exception("Failed to load History Data from database.")

        finally:
            conn.rollback()
            self.db_manager.release_connection(conn)

    

    
