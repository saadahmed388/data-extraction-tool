from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

from core.models.data_models import ReportPayload

import logging
logger = logging.getLogger(__name__)

    

class PostgresHistoryManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_history(self):
        
        conn = None
        
        try:
            conn = self.db_manager.get_connection()
        
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        row_id,
                        sr_num,
                        config_name,
                        status,
                        report,
                        created,
                        run_start_time,
                        run_end_time
                    FROM 
                        extraction.v_history_view
                """)
                data = cursor.fetchall()
                return data
                
        except Exception as e:
            logger.exception("Failed to load History Data from database.")
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def add_history_record(self, report_payload: ReportPayload):

        conn = None
        row_id = None
        
        try:
            conn = self.db_manager.get_connection()
            query = """
                INSERT INTO extraction.extraction_run_report (extn_run_id, sr_num, config_id, config_name, run_start_time, run_end_time, status, report)
                VALUES (%(sr_id)s, %(sr_num)s, %(config_id)s, %(config_name)s, %(run_start_time)s, %(run_end_time)s, %(status)s, %(report)s)
                RETURNING row_id
            """
            params = {
                "sr_id": report_payload.sr_id,
                "sr_num": report_payload.sr_num,
                "config_id": report_payload.config_id,
                "config_name": report_payload.config_name,
                "run_start_time": report_payload.start_time,
                "run_end_time": report_payload.end_time,
                "status": "Completed",
                "report": report_payload.report
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                print(count)
                row_id = cursor.fetchone()[0]
                logger.info(f"{count} row/s inserted")
            
            conn.commit()
            return row_id
                
        except Exception as e:
            logger.error("Failed to add history to the database due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Database rollback failed while handling an insertion failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)




