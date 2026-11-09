<<<<<<< HEAD
=======
from __future__ import annotations
from typing import TYPE_CHECKING
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime 
from core.data_models import NewQueryPayload, UpdateQueryPayload, UpdateQueryClassPayload, RemoveQueryPayload
from core.exceptions import NotFound, InsertionError

import logging
import json
import os

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.postgres_managers.query_manager import PostgresQueryManager

import json
import os

class QueryManager(QObject):

    queries_updated = pyqtSignal()

    def __init__(self, postgres_query_manager: PostgresQueryManager):

        super().__init__()
        self.postgres_query_manager = postgres_query_manager
        query_data = self.postgres_query_manager.load_queries()
        self.queries = QueryManager.group_data(query_data)

    @property
    def all_queries(self):
        return self.queries

    @staticmethod
    def group_data(data):

        json_list = []

        for d in data:
            json_list.append({
                "id": d[0],
                "name": d[1],
                "sql": d[2],
                "class": d[3],
                "is_active": d[4],
                "date_added_on": d[5],
                "date_modified_on": d[6]
            })

        return json_list

    @property
    def query_names(self):
        return [q["name"] for q in self.queries]

    @property
    def query_name_id_map(self):
        return {q["name"]: q["id"] for q in self.queries}

    def add_query(self, new_query_payload: NewQueryPayload) -> bool:
            
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query_name = new_query_payload.name
            query = new_query_payload.sql
            query_id = self.postgres_query_manager.add_query(new_query_payload)
            
            if not query_id:
                raise InsertionError(f"Failed to add Query: {query_name}")
            
            self.queries.append({
                "id": query_id,
                "name": query_name, 
                "sql": query, 
                "date_added_on": timestamp,
                "date_modified_on": timestamp
            })

            self.queries_updated.emit()
            return True

        except Exception as e:

            logger.error(f"Failed to add query {query_name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to add query({type(e).__name__}: {e}).") from e 


    def remove_query(self, remove_query_payload: RemoveQueryPayload) -> bool:

        try:

            id = remove_query_payload.id
            name = remove_query_payload.name

            self.postgres_query_manager.remove_query(id)
    
            self.queries = [
                q for q in self.queries 
                if q["id"] != id
            ]

            self.queries_updated.emit()
            return True

        except Exception as e:

            logger.error(f"Failed to delete query {name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to delete query ({type(e).__name__}: {e}).") from e 

    def update_query(self, update_query_payload: UpdateQueryPayload):

        try:

            id = update_query_payload.id
            name = update_query_payload.name
            query = update_query_payload.sql

            self.postgres_query_manager.update_query(update_query_payload)

            payload = next((q for q in self.queries if q["id"] == id), None)

            if not payload:
                raise NotFound("Query not found in cache")

            payload["name"] = name
            payload["sql"] = query

            self.queries_updated.emit()
            return True

        except Exception as e:

            logger.error(f"Failed to update query {name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update query ({type(e).__name__}: {e}).") from e         


    def update_query_class(self, update_query_class_payload: UpdateQueryClassPayload) -> bool:
        
        try:
            
            self.postgres_query_manager.update_query_class(update_query_class_payload)

            query_id = update_query_class_payload.id
            query_name = update_query_class_payload.name
            query_class = update_query_class_payload.query_class
            
            query = ((next(q) for q in self.queries if q["id"] == query_id))
            
            if not query:
                raise NotFound("Query not found in cache")

            query["class"] = query_class

            self.queries_updated.emit()
            return True

        except Exception as e:
            
            logger.error(f"Failed to update class for query {query_name} at the application layer", exc_info=True)
            raise RuntimeError(f"Unable to update query class ({type(e).__name__}: {e}).") from e 
        
