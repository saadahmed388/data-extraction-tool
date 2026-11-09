<<<<<<< HEAD
from PyQt5.QtCore import QObject, pyqtSignal
from core.db_client import DBClient
=======
from __future__ import annotations
from PyQt5.QtCore import QObject, pyqtSignal
from core.db_client import DBClient
from typing import TYPE_CHECKING
from core.data_models import NewConnectionPayload, UpdateConnectionPayload, RemoveConnectionPayload
from core.exceptions import NotFound, InsertionError
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)

import logging
import json
import os

if TYPE_CHECKING:
    from core.postgres_managers.connection_manager import PostgresConnectionManager

logger = logging.getLogger(__name__)

class ConnectionManager(QObject):
    connections_updated = pyqtSignal()
    def __init__(self, postgres_connection_manager: PostgresConnectionManager):
        
        super().__init__()
        self.postgres_connection_manager = postgres_connection_manager
        connections_data = self.postgres_connection_manager.load_connections()
        self.connections = ConnectionManager.group_data(connections_data)
        
        self.connections_updated.connect(self.load_connections)
        
        self.load_connections()
        self.db_clients = {}
        self.connect_all()

    @staticmethod
    def group_data(data):
        grouped_data = []

        for d in data:
            grouped_data.append({
                "id" : d[0],
                "name" : d[1],
                "user": d[2],
                "password": d[3],
                "dsn": d[4]
            })
            
        return grouped_data

    def load_connections(self):
        connections_data = self.postgres_connection_manager.load_connections()
        self.connections = ConnectionManager.group_data(connections_data)

    @property
    def all_connections(self):
        return self.connections

    @property
    def all_clients(self):
        return self.db_clients
    
    @property
    def connection_names(self):
        return [c["name"] for c in self.connections]
    
    @property
    def connection_name_id_map(self):
        return {c["name"]: c["id"] for c in self.connections}         
    
    def add_connection(self, new_connection_payload: NewConnectionPayload):

        connection = None
        registered = False

        try:

            name = new_connection_payload.name
            username = new_connection_payload.user
            password = new_connection_payload.password
            dsn = new_connection_payload.dsn

            connection = DBClient(
                user=username,
                password=password,
                dsn=dsn
            )

            self.test_pool(connection.pool, name)
            connection_id = self.postgres_connection_manager.add_connection(new_connection_payload)

            if not connection_id:
                raise InsertionError(f"Failed to add Query: {name}")

            self.db_clients[name] = connection

            self.connections.append({
                "id" : connection_id,
                "name" : name,
                "user" : username,
                "password" : password,
                "dsn" : dsn
            })

            registered = True
            self.connections_updated.emit()
            return True

        except Exception as e:

            logger.error(f"Failed to add connection {name} | DSN: {dsn} due to an unexpected error.", exc_info=True)
            raise RuntimeError(f"Failed to add a connection into the database ({type(e).__name__}: {e}).") from e

        finally:
            if not registered and connection is not None:
                try:
                    connection.close()
                except Exception as e:
                    logger.error(f"Failed to clean up connection: {name}", exc_info=True)
    
    def remove_connection(self, remove_connection_payload: RemoveConnectionPayload):
        
        try:

            id = remove_connection_payload.id
            name = remove_connection_payload.name
      
            self.postgres_connection_manager.remove_connection(remove_connection_payload)

            client = self.db_clients.pop(id, None)
            
            if client is not None:
                client.close_pool()

            self.connections = [
                con for con in self.connections 
                if con["id"]!= id
            ]

            self.connections_updated.emit()

            return True

        except Exception as e:
            logger.error(f"Failed to remove connection {name} due to an unexpected error.", exc_info=True)
            raise RuntimeError(f"Failed to remove connection ({type(e).__name__}: {e}).") from e

    def update_connection(self, update_connection_payload: UpdateConnectionPayload):
        
        connection = None
        registered = False

        try:

            payload = update_connection_payload

            id = payload.id
            name = payload.name
            username = payload.user
            password = payload.password
            dsn = payload.dsn
            

            connection = DBClient(
                user=username,
                password=password,
                dsn=dsn
            )

            self.test_pool(connection.pool, name)
            self.postgres_connection_manager.update_connection(update_connection_payload)

            self.db_clients[id] = connection

            con = next((c for c in self.connections if c["id"] == id), None)

            if not con:
                raise NotFound("Connection not found in cache")
            
            con["name"] = name
            con["user"] = username
            con["password"] = password
            con["dsn"] = dsn 
            
            registered = True
            self.connections_updated.emit()
            return True

        except Exception as e:
            
            logger.error(f"Failed to modify connection due to an unexpected error.", exc_info=True)
            raise RuntimeError(f"Failed to add a connection into the database ({type(e).__name__}: {e}).") from e

        finally:

            if not registered and connection is not None:

                try:
                    connection.close()
                except Exception as e:
                    logger.error(f"Failed to clean up connection: {name}", exc_info=True)
            

    def connect_all(self):

        for c in self.connections:
            
            id = c["id"]
            name = c["name"]
            username = c["user"]
            password = c["password"]
            dsn = c["dsn"]

            try:
                connection = DBClient(
                    user=username,
                    password=password,
                    dsn=dsn
                )
            
                pool = connection.pool
                if self.test_pool(pool, name):            
                    self.db_clients[id] = connection 
            
            except Exception as e:
                logger.error(f"""
                    Connection failed for environment : {name}
                    Description : {e}
                """, exc_info=True)
                raise e
        
    def test_pool(self, pool, env):

        try:
            with pool.acquire() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM dual")
            logger.info(f"{env} pool OK")
            return True
        
        except Exception as e:
            logger.error(f"{env} pool FAILED: {e}", exc_info=True)
            raise e


    
    
        
        
        
        
        
        