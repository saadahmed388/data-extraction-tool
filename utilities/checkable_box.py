from PyQt5.QtWidgets import QComboBox, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal
from utilities.stylesheets import StylingManager

class CheckableComboBox(QComboBox):

    item_pressed = pyqtSignal(dict)

    def __init__(self, all_items, checked_items, name_id_map):

        super().__init__()
        self.styling_manager = StylingManager()
        
        self.setView(QListView())
        self.setModel(QStandardItemModel(self))
        self.setObjectName("export_configs_selector")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self.styling_manager.selector_box_style("export_configs_selector"))
        self.view().setStyleSheet(self.styling_manager.selector_style())
        self.view().pressed.connect(self.handleItemPressed)
        
        self.addCheckItems(all_items, checked_items, name_id_map)
        self.checked = self.load_checked()

    def load_checked(self):

        checked  = {}
        model = self.model()
        row_count = model.rowCount()

        for ind in range(row_count):

            model_index = model.index(ind, 0)    
            item = self.model().itemFromIndex(model_index)
            
            item_id = item.data(Qt.ItemDataRole.UserRole)
            item_text = item.text()
            
            if item.checkState() == Qt.Checked:
                checked[item_id] = item_text

        return checked
            

    def addCheckItems(self, all_items, checked_items, name_id_map):
        
        for it in all_items:
        
            item = QStandardItem(it)
        
            item.setFlags((item.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsTristate)            
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            item.setData(name_id_map[it], Qt.ItemDataRole.UserRole)

            if it in checked_items:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            
            self.model().appendRow(item)

    def handleItemPressed(self, index):

        item = self.model().itemFromIndex(index)
        item_id = item.data(Qt.ItemDataRole.UserRole)
        item.setFlags((item.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsTristate)
        
        if item.checkState():
            item.setCheckState(Qt.Unchecked)
            self.checked.pop(item_id, None)
            mode = "remove"
        else:
            item.setCheckState(Qt.Checked)
            self.checked[item_id] = item.text()
            mode = "add"

        payload = {
            "list": self.checked,
            "item_id": item_id,
            "item_name": item.text(),
            "mode": mode
        }

        self.item_pressed.emit(payload)


