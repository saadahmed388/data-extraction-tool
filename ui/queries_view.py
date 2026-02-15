# ---------------- ui/queries_view.py ----------------
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog, QComboBox, QListView,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt
from utilities.sql_formatting import SqlPreview
from utilities.custom_widgets import StyledInputDialog
from datetime import datetime

class QueriesTab(QWidget):
    def __init__(self, db_clients, query_manager, styling_manager):
        super().__init__()
        self.db_clients = db_clients
        self.query_manager = query_manager
        self.styling_manager = styling_manager

        layout = QVBoxLayout()
        self.tree = QTreeWidget()        
        self.tree.setHeaderLabels(['Query Name', 'Class', 'SQL', 'Added On', 'Modified On'])
        self.tree.setIndentation(0)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(3, 200)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        
        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()
        self.add_btn = QPushButton('Add Extraction Query')
        self.modify_btn = QPushButton('Modify Query')
        self.delete_btn = QPushButton('Delete Query')
        self.add_class_btn = QPushButton('Add Class')
        self.delete_class_btn = QPushButton('Remove Class')
        button_bar.addWidget(self.add_btn)
        button_bar.addWidget(self.modify_btn)
        button_bar.addWidget(self.delete_btn)
        button_bar.addWidget(self.add_class_btn)
        button_bar.addWidget(self.delete_class_btn)        
        self.add_btn.setStyleSheet(self.styling_manager.button_style())
        self.modify_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_btn.setStyleSheet(self.styling_manager.button_style())
        self.add_class_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_class_btn.setStyleSheet(self.styling_manager.button_style())
        layout.addLayout(button_bar)
        #button_bar_widget = QWidget()
        #button_bar_widget.setLayout(button_bar)
        #button_bar_widget.setStyleSheet(self.styling_manager.button_bar_style())
        
       
        self.setLayout(layout)
        
        self.sql_queries = {}        
        self.add_btn.clicked.connect(self.add_query)
        self.modify_btn.clicked.connect(self.modify_query)
        self.delete_btn.clicked.connect(self.delete_query)
        #self.add_class_btn.clicked.connect(self.add_class)
        #self.delete_class_btn.clicked.connect(self.delete_class)
        self.query_manager.queries_updated.connect(self.load_queries)
        self.load_queries()
        #self.classes = self.load_classes()
    

    def add_query(self):
        name, ok1 = StyledInputDialog('Query Name', 'Enter extraction query name:').get_text()
        if not ok1 or not name:
            return
        sql, ok2 = StyledInputDialog('SQL', 'Enter query:', num_lines = "M").get_text()
        if not ok2 or not sql:
            return
        self.query_manager.add_query(name, sql)
        #item = QTreeWidgetItem([name, sql])
        #self.tree.addTopLevelItem(item)
        QMessageBox.information(self, 'Added', f'Query {name} added')
    
    def modify_query(self):
        selected = self.tree.currentItem()
        
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a query to edit.")
            return
        
        queries = self.query_manager.get_all_queries()
        old_name = selected.text(0)
        for q in queries: 
            if q["name"] == old_name: 
                old_sql = q["sql"]

        new_name, ok1 = StyledInputDialog('Query Name', 'Modify query name:', default_text = old_name).get_text()
        #new_name, ok1 = QInputDialog.getText(self, 'Query Name', 'Modify query name:', text=old_name)
        new_sql, ok2 = StyledInputDialog('SQL', 'Modify extraction query:', default_text = old_sql, num_lines = "M").get_text()
        #new_sql, ok2 = QInputDialog.getMultiLineText(self, 'SQL', 'Modify extraction query:', text=old_sql)
        
        for q in queries:
            if q["name"] == old_name and q["sql"] == old_sql:
                if(new_name != old_name or new_sql != old_sql):
                    q["date_modified_on"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if ok1 and new_name.strip():
                    q["name"] = new_name.strip()
                if ok2 and new_sql.strip():
                    q["sql"] = new_sql.strip()
                break

        self.query_manager.save_queries()
        
    def delete_query(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a query to delete.")
            return
        
        name = selected.text(0)
        
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete query '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        self.query_manager.delete_query(name)
        self.query_manager.save_queries()
        self.query_manager.load_queries()
        
    def load_queries(self):
        self.tree.clear()
        queries = self.query_manager.get_all_queries()
        if queries:
            for q in queries:
                name = q.get("name", "")
                sql = q.get("sql", "")
                query_class = q.get("class", "")
                date_added_on = q.get("date_added_on", "")
                date_modified_on = q.get("date_modified_on", "")
                
                self.sql_queries[name] = sql
                
                item = QTreeWidgetItem([name, '', '', date_added_on, date_modified_on])
                self.tree.addTopLevelItem(item)
                    
                # 🔍 Preview button
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                preview_btn.clicked.connect(lambda _, q=name: self.show_sql(q))
                self.tree.setItemWidget(item, 2, preview_btn)
                
                # Class selector
                class_selector = QComboBox()
                class_selector.setView(QListView())                
                class_selector.setObjectName("class_selector")
                class_selector.setAttribute(Qt.WA_StyledBackground, True)
                class_selector.setStyleSheet(self.styling_manager.selector_box_style("class_selector"))
                class_selector.view().setStyleSheet(self.styling_manager.selector_style())
                class_names = ["Other", "CM", "VM"]            
                
                class_selector.addItems(class_names)
                index = class_selector.findText(query_class)
                if index != -1:
                    class_selector.setCurrentIndex(index)
                class_selector.currentTextChanged.connect(self.dynamic_save)
                self.tree.setItemWidget(item, 1, class_selector)

    def show_sql(self, q_name):
        self.preview_window = SqlPreview(self.sql_queries[q_name])
        self.preview_window.show()
    
    def dynamic_save(self):
        selected_item = self.tree.currentItem()
        
        ## Query Class
        class_selector = self.tree.itemWidget(selected_item, 1)
        selected_class = class_selector.currentText()
        
        ##Query Name
        query_name = selected_item.text(0)
        
        queries = self.query_manager.get_all_queries()
        for q in queries:
            if q["name"] == query_name:
                q["class"] = selected_class
                break
        
        self.query_manager.save_queries()
            
            
        
       
        
