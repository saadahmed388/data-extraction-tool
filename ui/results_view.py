# ================= ui/results_view.py =================
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout
)
from PyQt5.QtCore import Qt



class ResultsTab(QWidget):
    def __init__(self, db_clients, staging_manager, query_manager, styling_manager, connections_tab, queries_tab):
        super().__init__()
        self.db_clients = db_clients
        self.staging_manager = staging_manager
        self.query_manager = query_manager
        self.styling_manager = styling_manager
        self.connections_tab = connections_tab
        self.queries_tab = queries_tab
  
        layout = QVBoxLayout()
              
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Preset Name', ''])
        self.tree.setIndentation(0)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 600)
        self.tree.setColumnWidth(2, 250)
        self.tree.setColumnWidth(3, 250)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        
        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()
        self.run_btn = QPushButton('Run All Monitoring Queries')
        self.run_btn.setStyleSheet(self.styling_manager.button_style())
        button_bar.addWidget(self.run_btn)
        layout.addLayout(button_bar)
        
        self.setLayout(layout)
        self.results_map = {}
        
        self.run_btn.clicked.connect(self.run_all_queries)

    def run_all_queries(self):
        self.tree.clear()
        total_found = 0      
        
        for env, client in self.db_clients.items():
            self.active_connections = self.connections_tab.get_active_connections()
            print(self.active_connections)
            if env not in self.active_connections:
                continue
            
            queries = self.query_manager.get_all_queries()
            if not queries:
                QMessageBox.information(self, "No Queries Added", "Please add monitoring queries first.")
                return
                
            for query_def in queries:
                query_name = query_def['name']
                query_sql = query_def['sql']
                self.active_queries = self.queries_tab.get_active_queries()
                if query_name not in self.active_queries:
                    continue
                try:
                    # ✅ Execute the monitoring SQL
                    results = client.execute_select(query_sql)
                    
                    if not results:
                        continue  # nothing found
                        
                    # store results for later table view
                    self.results_map[(env, query_name)] = results

                    # add row
                    item = QTreeWidgetItem([env, query_name, '', ''])
                    self.tree.addTopLevelItem(item)

                    # 🔍 Preview button
                    preview_btn = QPushButton()
                    preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                    preview_btn.setFlat(True)
                    #preview_btn.setText("View")
                    preview_btn.clicked.connect(lambda _, e=env, q=query_name: self.show_table(e, q))
                    self.tree.setItemWidget(item, 2, preview_btn)

                    # ✅ Stage checkbox
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(3, Qt.Checked)

                    for row in results:
                        # Stage result for recovery
                        self.staging_manager.stage_change(
                            env=env,
                            query_name=query_name,
                            row_data=row,
                            sql_template = query_sql   
                        )
                        #row_item = QTreeWidgetItem([env, query_name, str(row), 'Stage'])
                        #row_item.setFlags(row_item.flags() | Qt.ItemIsUserCheckable)
                        #row_item.setCheckState(3, Qt.Checked)
                        #self.tree.addTopLevelItem(row_item)
                
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Query Execution Failed",
                        f"Error running '{query_name}' on {env}:\n{str(e)}"
                    )
                
        QMessageBox.information(self, 'Run Complete', 'All monitoring queries executed')
        
    def show_table(self, env, query_name):
        """Display the query result as a table in a popup."""
        rows = self.results_map.get((env, query_name), [])
        if not rows:
            QMessageBox.information(self, "No Data", "No rows available for this query.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{env} - {query_name}")
        dialog.resize(800, 400)

        layout = QVBoxLayout(dialog)

        table = QTableWidget(len(rows), len(rows[0]))
        table.setHorizontalHeaderLabels(list(rows[0].keys()))
        table.setStyleSheet(self.styling_manager.header_style())

        for i, row in enumerate(rows):
            for j, col in enumerate(row.keys()):
                table.setItem(i, j, QTableWidgetItem(str(row[col])))

        table.resizeColumnsToContents()
        
        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet(self.styling_manager.button_style())
        layout.addWidget(close_btn)

        dialog.exec_()

