# ---------------- ui/queries_view.py ----------------
from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QComboBox, QListView,
    QMessageBox, QStyle, QHBoxLayout, QDialog
)
from PyQt5.QtCore import Qt
from utils.sql_formatter import SqlPreview
from utils.styled_input_dialog import SingleLineInputDialog, MultiLineInputDialog
from utils.selector_dialog import SelectorDialog
from utils.permission_dialog import PermissionDialog

from typing import TYPE_CHECKING

from core.models.data_models import (
    NewQueryPayload, RemoveQueryPayload, 
    UpdateQueryPayload, UpdateQueryClassPayload
)

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.managers.query_manager import QueryManager

class QueriesTab(QWidget):
    def __init__(self, query_manager: QueryManager, styling_manager):
        super().__init__()

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
        self.update_btn = QPushButton('Modify Query')
        self.delete_btn = QPushButton('Delete Query')
        self.add_class_btn = QPushButton('Add Class')
        self.delete_class_btn = QPushButton('Remove Class')
        button_bar.addWidget(self.add_btn)
        button_bar.addWidget(self.update_btn)
        button_bar.addWidget(self.delete_btn)
        button_bar.addWidget(self.add_class_btn)
        button_bar.addWidget(self.delete_class_btn)        
        self.add_btn.setStyleSheet(self.styling_manager.button_style())
        self.update_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_btn.setStyleSheet(self.styling_manager.button_style())
        self.add_class_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_class_btn.setStyleSheet(self.styling_manager.button_style())
        layout.addLayout(button_bar)        
       
        self.setLayout(layout)
        
        self.sql_queries = {}        
        self.add_btn.clicked.connect(self.add_query)
        self.update_btn.clicked.connect(self.update_query)
        self.delete_btn.clicked.connect(self.remove_query)
        self.query_manager.queries_updated.connect(self.load_queries)

        self.load_queries()    

    def add_query(self):
        
        try:

            name, ok1 = SingleLineInputDialog('Query Name', 'Enter query name:').get_text()
            if not ok1 or not name:
                return
            
            sql, ok2 = MultiLineInputDialog('SQL', 'Enter query:').get_text()
            if not ok2 or not sql:
                return

            q_class_list = ["CM", "VM", "Other"]
            q_class = SelectorDialog("Query Class Selector", "Select Query Class: ", q_class_list)
            
            if q_class.exec_() == QDialog.Rejected:
                return
            q_class_name = q_class.get_selected_item() or None

            new_query_payload = NewQueryPayload(
                name = name,
                sql = sql,
                query_class = q_class_name
            )
            
            self.query_manager.add_query(new_query_payload)

            QMessageBox.information(self, 'Added', f'Query {name} added')

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
    
    def update_query(self):

        try:

            selected = self.tree.currentItem()
            
            if not selected:
                QMessageBox.warning(self, "No Selection", "Please select a query to update.")
                return

            id = selected.data(0, Qt.ItemDataRole.UserRole)
            old_name = selected.text()
            old_sql = self.sql_queries[id]
            

            new_name, ok1 = SingleLineInputDialog('Query Name', 'Update query name:', default_text = old_name).get_text()

            if not new_name or not ok1:
                return

            new_sql, ok2 = MultiLineInputDialog('SQL', 'Update extraction query:', default_text = old_sql).get_multiline_text()

            if not new_sql or not ok2:
                return

            update_query_payload = UpdateQueryPayload(
                id=id,
                name=new_name,
                sql=new_sql
            )

            self.query_manager.update_query(update_query_payload)          

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
        
    def remove_query(self):

        try:

            selected = self.tree.currentItem()

            if not selected:
                QMessageBox.warning(self, "No Selection", "Please select a query to remove.")
                return
            
            name = selected.text(0)
            id = selected.data(0, Qt.ItemDataRole.UserRole)

            remove_query_payload = RemoveQueryPayload(
                id = id,
                name = name
            )

            p_dialog = None

            try:
                                        
                msg_str = f"Are you sure to delete the query...?"
                p_dialog = PermissionDialog(msg_str, self.styling_manager)
                action = p_dialog.exec()
                if not action:
                    return

            finally:

                if p_dialog is not None:
                    p_dialog.deleteLater()

            self.query_manager.remove_query(remove_query_payload)

            QMessageBox.information(self, "Information", "Query deleted successfully")

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
        
    def load_queries(self):

        try:

            self.tree.clear()
            queries = self.query_manager.all_queries

            if not queries: 
                return
            
            for q_id, q_details in queries.items():

                id = q_id
                name = q_details.get("name", "")
                sql = q_details.get("sql", "")
                query_class = q_details.get("class", "")
                date_added_on = q_details.get("date_added_on", "")
                date_modified_on = q_details.get("date_modified_on", "")
                
                self.sql_queries[id] = sql
                
                item = QTreeWidgetItem([name, '', '', date_added_on, date_modified_on])
                item.setData(0, Qt.ItemDataRole.UserRole, id)
                self.tree.addTopLevelItem(item)
                    
                # 🔍 Preview button
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                preview_btn.clicked.connect(lambda _, id=id: self.show_sql_query(id))
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
                class_selector.currentTextChanged.connect(self.update_query_class)
                self.tree.setItemWidget(item, 1, class_selector)

        except Exception as e:
        
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
                
    def update_query_class(self):
        
        try:

            selected_item = self.tree.currentItem()
            class_selector = self.tree.itemWidget(selected_item, 1)

            query_id = selected_item.data(0, Qt.ItemDataRole.UserRole)
            query_name = selected_item.text(0)            
            query_class = class_selector.currentText()

            update_query_class_payload = UpdateQueryClassPayload(
                id=query_id,
                name=query_name,
                query_class=query_class
            )

            p_dialog = None

            try:
                                        
                msg_str = f"Are you sure to update the query class...?"
                p_dialog = PermissionDialog(msg_str, self.styling_manager)
                action = p_dialog.exec()
                if not action:
                    return

            finally:

                if p_dialog is not None:
                    p_dialog.deleteLater()

            self.query_manager.update_query_class(update_query_class_payload)

            QMessageBox.information(self, "Information", "Query class update successfully...")

        except Exception as e:

            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)

    
    def show_sql_query(self, id):
        
        try:
            
            self.preview_window = SqlPreview(self.sql_queries[id])
            self.preview_window.show()

        except Exception as e:
        
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            user_msg = f"<b>An error occurred:</b> {e}<br><br><i>Check logs for full traceback.</i>"
            QMessageBox.critical(self, "Error", user_msg)
        
            
    
            
            
        
       
        
