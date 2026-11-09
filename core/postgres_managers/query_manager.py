from __future__ import annotations
from typing import TYPE_CHECKING
from core.data_models import (
    NewQueryPayload, UpdateQueryPayload, 
    RemoveQueryPayload, UpdateQueryClassPayload
)

if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

import logging
logger = logging.getLogger(__name__)

class PostgresQueryManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_queries(self):
        conn = None
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        row_id,
                        name,
                        sql,
                        class,
                        is_active,
                        to_char(created, 'DD-MM-YYYY HH24:MI:SS') AS created,
                        to_char(last_updated, 'DD-MM-YYYY HH24:MI:SS') AS last_updated
                    FROM extraction.queries
                """)
                data = cursor.fetchall()
                return data
                
        except Exception as e:
            logger.error("Failed to load queries data from database due to unexpected error", exc_info=True)
            raise RuntimeError(f"Failed to load the queries data from database ({type(e).__name__} : {e}).\nCheck logs for full traceback")


        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def add_query(self, new_query_payload: NewQueryPayload) -> bool:
        conn = None
        row_id = None
        try:
            conn = self.db_manager.get_connection()
            query = """
                INSERT INTO extraction.queries (name, sql)
                VALUES (%s, %s)
                RETURNING row_id
            """
            params = (
                new_query_payload.name,
                new_query_payload.sql
            )

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                row_id = cursor.fetchone()[0]
                logger.info(f"{count} rows/s inserted")
            
            conn.commit()
            return row_id
                
        except Exception as e:
            
            logger.error("Failed to add query due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an insertion failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def remove_query(self, remove_query_payload: RemoveQueryPayload) -> bool:

        conn = None

        try:

            id = remove_query_payload.id
            name = remove_query_payload.name

            query = """
                DELETE FROM extraction.queries 
                WHERE row_id = %s
                RETURNING name
            """
            params = (id,)

            conn = self.db_manager.get_connection()
            
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                q_name = cursor.fetchone()[0]
                logger.info(f"{count} row/s deleted | Name: {q_name}")

            if count == 0:
                logger.warning(
                    "No query found to be deleted | Name: %s",
                    name
                )
                return False
            
            conn.commit()
            return True           
        
        except Exception as e:
            
            logger.error("Failed to delete query due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling a deletion failure.", exc_info=rollback_err)
            
            raise e
        
        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def update_query(self, update_query_payload: UpdateQueryPayload):
        
        conn = None
        
        try:

            conn = self.db_manager.get_connection()
            query = """
                UPDATE 
                    extraction.queries 
                SET 
                    name = %(name)s,
                    sql = %(sql)s
                WHERE 
                    row_id = %(id)s
                RETURNING name
            """

            params = {
                "id": update_query_payload.id,
                "name": update_query_payload.name,
                "sql": update_query_payload.sql
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                q_name = cursor.fetchone()[0]
                logger.info(f"{count} row/s updated | Name: {q_name}")
            
            conn.commit()
            return True
                
        except Exception as e:

            logger.error("Failed to update query due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an update failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)
         

    def update_query_class(self, update_query_class_payload: UpdateQueryClassPayload) -> bool:
        conn = None
        try:
            conn = self.db_manager.get_connection()

            query_id = update_query_class_payload.id
            query_class = update_query_class_payload.query_class

            query = """
                UPDATE extraction.queries 
                SET class = %(query_class)s
                WHERE row_id = %(id)s
                RETURNING name
            """
            params = {
                "id" : query_id,
                "query_class" : query_class
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                q_name = cursor.fetchone()[0]
                logger.info(f"{count} row/s updated | Name: {q_name}")
            
            conn.commit()
            return True
                
        except Exception as e:

            logger.error("Failed to update query class due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Rollback failed during handling an update failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    




