from PyQt5.QtCore import QObject, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

class ExtractionWorker(QObject):

    error = pyqtSignal(Exception)
    progress = pyqtSignal(str) 
    finished = pyqtSignal(list)

    def __init__(self, preset_items, queries, db_clients, base_folder_path):
        super().__init__()
        
        self.preset_items = preset_items
        self.queries = queries
        self.db_clients = db_clients
        self.base_folder_path = base_folder_path
        
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):

        try:
            tasks = []
            report = []
    
            with ThreadPoolExecutor(max_workers=8) as executor:

                for preset_item in self.preset_items:
                    if self._is_running:
                        future = executor.submit(
                            self.process_item, 
                            preset_item, 
                            self.base_folder_path 
                        )
                        tasks.append(future)

                for future in as_completed(tasks):
                    if not self._is_running:
                        self.progress.emit('Extraction Cancelled') 
                        return
                    try:
                        result = future.result()
                        if result:
                            report.append(result)
                    except Exception as e:
                        logger.error(str(e))
                        self.error.emit(e) 
                        return
            
            self.finished.emit(report)   

        except Exception as e:
            
            logger.exception(f"Execution failed in Thread pool")
            self.error.emit(e) 

    def process_item(self, preset_item, base_folder_path):

        print(self.queries)

        try:
            con_name = preset_item.get("con_name", None)
            con_id = preset_item.get("con_id", None) 

            query_name = preset_item.get("query_name", None)
            query_id = preset_item.get("query_id", None)

            dbc_obj = self.db_clients[con_id]
            query = self.queries[query_id]["sql"]            
            class_name = self.queries[query_id]["class"]

            class_folder_path = os.path.join(base_folder_path, class_name)
            if not os.path.exists(class_folder_path):
                os.makedirs(class_folder_path, exist_ok=True)
            
            file_name = f'{con_name}.csv'
            file_path = os.path.join(class_folder_path, file_name)
            
            print('\n')
            logger.info(f'Execution Started || ENV: {con_name} || SQL: {query_name} || Class: {class_name}')
            
            rows, cols = dbc_obj.execute_select(query)
            
            df = pd.DataFrame(rows, columns=cols, dtype=str)
            df.to_csv(file_path, index=False, encoding='utf-8')
            record_count = len(rows)
            
            print(df.head())
            
            logger.info(f'Execution Successful || ENV: {con_name} || SQL: {query_name} || Class: {class_name} || Count: {record_count}')
            report_item = {'env': con_name, 'sql_name': query_name, 'record_count': record_count}
            
            return report_item

        except Exception as e:

            logger.exception(f"Execution failed for preset item || ENV: {preset_item.get("con_id")} || SQL: {preset_item.get("query_id")}")
            raise e