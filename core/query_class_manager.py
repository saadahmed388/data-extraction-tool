class QueryClassManager:
    def __init__(self):
        

    def save_classes(self):
            class_file_path = 'data_and_config_files/classes.json'
            if not os.path.exists(class_file_path):
                os.makedirs(class_file_path, exists_ok = True)
            
            with open(class_file_path) as f:
                json.dump(self.classes, f)
                
        
    def load_classes(self):
        class_file_path = 'data_and_config_files/classes.json'
        if not os.path.exists(class_file_path):
            os.makedirs(class_file_path, exists_ok = True)
        
        with open(class_file_path) as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
            else:
                return []

    def add_class(self):
        class_name, ok1 = QInputDialog.getText(self, 'Class Name', 'Enter New Class name:')
        if not ok1 or not class_name:
            return
        
        if class_name in self.classes
            QInputDialog.information(self, 'Class Name', 'Class already exists! Please enter a new class')
            return
        
        self.classes.append(class_name)
        self.save_classes
        QInputDialog.information(self, 'Class Name', f'Class {class_name} added')
        return
                
        
    def delete_class(self):

    def 