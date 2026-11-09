from PyQt5.QtCore import QObject, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

class ExtractionWorker(QObject):

    error = pyqtSignal(str)
    progress = pyqtSignal(str) 
    finished = pyqtSignal(list)

    def __init__(self, preset_list, presets, base_folder_path, sql_list, db_clients):
        super().__init__()
        self.preset_list = preset_list
        self.presets = presets
        self.base_folder_path = base_folder_path
        self.sql_list = sql_list
        self.db_clients = db_clients
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        tasks = []
        info_list = []
  
        with ThreadPoolExecutor(max_workers=8) as executor:
            for preset in self.preset_list:
                for item in self.presets[preset]:
                    if self._is_running:
                        future = executor.submit(
                            self.process_item, 
                            item, 
                            preset, 
                            self.base_folder_path, 
                            self.sql_list
                        )
                        tasks.append(future)

            for future in as_completed(tasks):
                    if not self._is_running:
                        self.progress.emit('Extraction Cancelled') 
                        return
                    try:
                        result = future.result()
                        if result:
                            info_list.append(result)
                    except Exception as e:
                        logger.error(str(e))
                        self.error.emit(str(e)) 
        
        self.finished.emit(info_list)   

    def process_item(self, item, preset, base_folder_path, sql_list):
        try:
            env = item.get("env")
            sql_name = item.get("sql")
            sql_list_item = [item for item in sql_list if item.get("name") == sql_name]
            dbc_obj = self.db_clients[env]
            
            class_folder_name = sql_list_item[0]['class']
            class_folder_path = os.path.join(base_folder_path, class_folder_name)
            if not os.path.exists(class_folder_path):
                os.makedirs(class_folder_path, exist_ok=True)
            
            file_name = f'{env}.csv'
            file_path = os.path.join(class_folder_path, file_name)
            sql = sql_list_item[0]['sql']
            
            print('\n')
            logger.info(f'Execution Started || ENV: {env} || SQL: {sql_name} || Class: {class_folder_name} || Preset: {preset}')
            
            rows, cols = dbc_obj.execute_select(sql)
            
            df = pd.DataFrame(rows, columns=cols, dtype=str)
            df.to_csv(file_path, index=False, encoding='utf-8')
            record_count = len(rows)
            
            print(df.head())
            
            logger.info(f'Execution Successful || ENV: {env} || SQL: {sql_name} || Class: {class_folder_name} || Preset: {preset} || Count: {record_count}')
            info_item = {'env': env, 'sql_name': sql_name, 'record_count': record_count}
            
            return info_item

        except Exception as e:
            logger.exception(f"Execution failed || ENV: {item.get("env")} || SQL: {item.get("sql")}")
            return {"error": str(e), "env": item.get("env")}