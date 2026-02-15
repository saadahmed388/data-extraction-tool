# ---------------- ui/main_window.py ----------------
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt5.QtGui import QIcon
from config.db_configs import ENVIRONMENTS, DB_CONFIGS
from core.db_config_manager import DBConfigManager
from core.db_client import DBClient
from core.staging import StagingManager
from ui.presets_view import PresetsTab
from ui.queries_view import QueriesTab
from ui.connections_view import ConnectionsTab
from ui.export_view import ExportsTab
from utilities.stylesheets import StylingManager
from ui.history_view import HistoryTab
from ui.export_configs_view import ExportConfigsTab
from core.query_manager import QueryManager
from core.export_configuration_manager import ExportConfigManager
from core.preset_manager import PresetManager
from core.history_manager import HistoryManager
from core.export_manager import ExportManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Extraction')
        self.setWindowIcon(QIcon("assets/data_extcn_app_icon.png"))
        self.resize(1400, 800)
        self.db_clients = {}
        self.db_config_manager = DBConfigManager()
        self.query_manager = QueryManager()
        self.styling_manager = StylingManager()
        self.preset_manager = PresetManager()
        self.history_manager = HistoryManager()
        self.export_manager = ExportManager()
        self.export_configuration_manager = ExportConfigManager()
        self.connections_tab = ConnectionsTab(self.db_clients, self.db_config_manager, self.styling_manager)
        self.queries_tab = QueriesTab(self.db_clients, self.query_manager, self.styling_manager)
        self.presets_tab = PresetsTab(self.query_manager, self.db_config_manager, self.styling_manager, self.preset_manager)
        self.export_configs_tab = ExportConfigsTab(self.db_config_manager, self.query_manager, self.styling_manager, self.history_manager, self.preset_manager, self.export_configuration_manager)
        self.exports_tab = ExportsTab(self.db_clients, self.db_config_manager, self.query_manager, self.styling_manager, self.history_manager, self.preset_manager, self.export_configuration_manager, self.export_manager)
        self.history_tab = HistoryTab(self.styling_manager, self.history_manager)

        tabs = QTabWidget()
        tabs.addTab(self.connections_tab, 'Connections')
        tabs.addTab(self.queries_tab, 'Extraction Queries')
        tabs.addTab(self.presets_tab, 'Presets')
        tabs.addTab(self.export_configs_tab, 'Export Configurations')
        tabs.addTab(self.exports_tab, 'Service Requests')
        tabs.addTab(self.history_tab, 'History')
        tabs.setStyleSheet(self.styling_manager.tab_style())
        
        self.setCentralWidget(tabs)
