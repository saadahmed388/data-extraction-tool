from __future__ import annotations
from typing import TYPE_CHECKING
from core.data_models import NewConnectionPayload, UpdateConnectionPayload, RemoveConnectionPayload
if TYPE_CHECKING:
    from core.postgres_managers.db_manager import PostgresDBManager

import logging
logger = logging.getLogger(__name__)

class PostgresConnectionManager:
    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager

    def load_connections(self):
        conn = None
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        row_id, 
                        name,
                        user_id,
                        password,
                        dsn
                    FROM 
                        extraction.connections
                """)
                data = cursor.fetchall()
                return data
                
        except Exception as e:
            logger.error("Failed to load connection data from database.", exc_info=True)
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def add_connection(self, new_connection_payload: NewConnectionPayload):
        conn = None
        row_id = None
        try:
            conn = self.db_manager.get_connection()
            query = """
                INSERT INTO extraction.connections (name, user_id, password, dsn)
                VALUES (%(name)s, %(user)s, %(password)s, %(dsn)s)
                RETURNING row_id
            """
            params = {
                "name": new_connection_payload.name,
                "user": new_connection_payload.user,
                "password": new_connection_payload.password,
                "dsn": new_connection_payload.dsn
            }

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                row_id = cursor.fetchone()[0]
                logger.info(f"{count} row/s inserted")
            
            conn.commit()
            return row_id
                
        except Exception as e:
            logger.error("Failed to add a connection to the database due to an unexpected error.", exc_info=True)

            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Database rollback failed while handling a deletion failure.", exc_info=rollback_err)
            
            raise e

        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)

    def remove_connection(self, remove_connection_payload: RemoveConnectionPayload):

        conn = None

        try:

            id = remove_connection_payload.id
            name = remove_connection_payload.name

            query = """
                DELETE FROM extraction.connections 
                WHERE row_id = %s
                RETURNING name
            """
            params = (id,)

            conn = self.db_manager.get_connection()
            
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                count = cursor.rowcount
                c_name = cursor.fetchone()[0]
                logger.info(f"{count} row/s deleted | Name: {c_name}")

            if count == 0:
                logger.warning(
                    "No connection found to be deleted | Name: %s",
                    name
                )
                return False
            
            conn.commit()
            return True            
        
        except Exception as e:

            logger.error("Failed to delete connection from database due to an unexpected error.", exc_info=True)
            
            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.error("Database rollback failed while handling a deletion failure.", exc_info=rollback_err)
            
            raise e
        
        finally:
            if conn is not None:
                self.db_manager.release_connection(conn)


    def update_connection(self, update_connection_payload: UpdateConnectionPayload):
    
            conn = None
    
            try:

                id = update_connection_payload.id
                name = update_connection_payload.name
                username = update_connection_payload.user
                password = update_connection_payload.password
                dsn = update_connection_payload.dsn
    
                query = """
                    UPDATE 
                        extraction.connections
                    SET
                        name = %(name)s,
                        user_id = %(username)s,
                        password = %(password)s,
                        dsn = %(dsn)s
                    WHERE
                        row_id = %(id)s
                    RETURNING name
                """

                params = {
                    "id" : id,
                    "name" : name,
                    "username" : username,
                    "password" : password,
                    "dsn" : dsn
                }
    
                conn = self.db_manager.get_connection()
                
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    count = cursor.rowcount
                    updated_query_name = cursor.fetchone()[0]
                    logger.info(f"{count} row/s updated | Name: {updated_query_name}")
    
                if count == 0:
                    logger.warning(
                        "No connection found to be updated | Name: %s",
                        name
                    )
                    return False
                
                conn.commit()
                return True            
            
            except Exception as e:
    
                logger.error("Failed to udpate connection from database due to an unexpected error.", exc_info=True)
                
                if conn is not None:
                    try:
                        conn.rollback()
                    except Exception as rollback_err:
                        logger.error("Database rollback failed while handling a deletion failure.", exc_info=rollback_err)
                
                raise e
            
            finally:
                if conn is not None:
                    self.db_manager.release_connection(conn)

            
    
