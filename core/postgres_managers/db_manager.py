import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

class PostgresDBManager:
    def __init__(self):
        self.connection_pool = self.create_pool()
        self.authenticate_pool_connection()

    def create_pool(self):
        try:
            connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=DATABASE_URL
            )
            return connection_pool

        except Exception as e:
            logger.error("Failed to created connection pool due to an unexpected error.", exc_info=True)
            raise e
            

    def authenticate_pool_connection(self):
        conn = None
        try:
            conn = self.connection_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        current_database(),
                        current_user,
                        inet_server_addr(),
                        inet_server_port(),
                        version()
                """)
                database, user, server_ip, server_port, version = cursor.fetchone()
            
            logger.info("SUCCESS: PostgreSQL connection established")
            logger.info(f"Database: {database}")
            logger.info(f"Authenticated user: {user}")
            logger.info(f"Server IP: {server_ip}")
            logger.info(f"Server port: {server_port}")
            logger.info(f"Server version: {version.split(",")[0]}")

        except Exception as e:
            logger.error("Failed to authenticate connection pool due to an unexpected error.", exc_info=True)
            raise e

        finally:
            if conn is not None:
                self.release_connection(conn)

    def get_connection(self):
            try:
                return self.connection_pool.getconn()
            except Exception as e:
                logger.error("Failed to get connection from the pool due to an unexpected error.", exc_info=True)
                raise e

    def release_connection(self, conn):
        try:
            self.connection_pool.putconn(conn)
        except Exception as e:
            logger.error("Failed to release connection back to the pool due to an unexpected error.", exc_info=True)
            raise e

