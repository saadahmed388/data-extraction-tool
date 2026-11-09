# ---------------- ui/main_window.py ----------------
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon

<<<<<<< HEAD
=======
from core.postgres_managers.db_manager import PostgresDBManager
from core.postgres_managers.connection_manager import PostgresConnectionManager
from core.postgres_managers.query_manager import PostgresQueryManager
from core.postgres_managers.preset_manager import PostgresPresetsManager
from core.postgres_managers.export_config_manager import PostgresExportConfigsManager
from core.postgres_managers.export_manager import PostgresExportManager
from core.postgres_managers.history_manager import PostgresHistoryManager

>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
from core.managers.connection_manager import ConnectionManager
from core.managers.query_manager import QueryManager
from core.managers.export_configuration_manager import ExportConfigManager
from core.managers.preset_manager import PresetManager
from core.managers.history_manager import HistoryManager
from core.managers.export_manager import ExportManager

from ui.presets_view import PresetsTab
from ui.queries_view import QueriesTab
from ui.connections_view import ConnectionsTab
from ui.export_view import ExportsTab
from ui.history_view import HistoryTab
from ui.export_configs_view import ExportConfigsTab

from utilities.stylesheets import StylingManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Extraction')
        self.setWindowIcon(QIcon("assets/data_extcn_app_icon.png"))
        self.resize(1400, 800)
<<<<<<< HEAD
        self.connection_manager = ConnectionManager()

        self.db_clients = self.connection_manager.get_all_clients()

        self.query_manager = QueryManager()
=======

        self.postgres_db_manager = PostgresDBManager()
        self.postgres_connection_manager = PostgresConnectionManager(self.postgres_db_manager)
        self.postgres_query_manager = PostgresQueryManager(self.postgres_db_manager)
        self.postgres_presets_manager = PostgresPresetsManager(self.postgres_db_manager)
        self.postgres_export_config_manager =PostgresExportConfigsManager(self.postgres_db_manager)
        self.postgres_export_manager = PostgresExportManager(self.postgres_db_manager)
        self.postgres_history_manager = PostgresHistoryManager(self.postgres_db_manager)
        
        self.connection_manager = ConnectionManager(self.postgres_connection_manager)
        self.query_manager = QueryManager(self.postgres_query_manager)
        self.preset_manager = PresetManager(self.postgres_presets_manager)
        self.export_configuration_manager = ExportConfigManager(self.postgres_export_config_manager)
        self.export_manager = ExportManager(self.postgres_export_manager)
        self.history_manager = HistoryManager(self.postgres_history_manager)
>>>>>>> 9e9615b (v2.0.0 - Major Backend Update - Postgres Integration)
        self.styling_manager = StylingManager()
        
        self.db_clients = self.connection_manager.all_clients
        
        self.connections_tab = ConnectionsTab(self.connection_manager, self.styling_manager)
        self.queries_tab = QueriesTab(self.query_manager, self.styling_manager)
        self.presets_tab = PresetsTab(self.preset_manager, self.connection_manager, self.query_manager, self.styling_manager)
        self.export_configs_tab = ExportConfigsTab(self.export_configuration_manager, self.query_manager, self.history_manager, self.preset_manager, self.styling_manager)
        self.exports_tab = ExportsTab(self.export_manager, self.db_clients, self.connection_manager, self.query_manager, self.history_manager, self.preset_manager, self.export_configuration_manager, self.styling_manager)
        self.history_tab = HistoryTab(self.history_manager, self.styling_manager)

        tabs = QTabWidget()
        tabs.addTab(self.connections_tab, 'Connections')
        tabs.addTab(self.queries_tab, 'Extraction Queries')
        tabs.addTab(self.presets_tab, 'Presets')
        tabs.addTab(self.export_configs_tab, 'Export Configurations')
        tabs.addTab(self.exports_tab, 'Service Requests')
        tabs.addTab(self.history_tab, 'History')
        tabs.setStyleSheet(self.styling_manager.tab_style())
        
        self.setCentralWidget(tabs)
