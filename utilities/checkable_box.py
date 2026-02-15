from PyQt5.QtWidgets import QComboBox, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from utilities.stylesheets import StylingManager

class CheckableComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setView(QListView())
        self.setModel(QStandardItemModel(self))
        self.checked = []
        self.styling_manager = StylingManager()
        self.setObjectName("export_configs_selector")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self.styling_manager.selector_box_style("export_configs_selector"))
        self.view().setStyleSheet(self.styling_manager.selector_style())
        self.view().pressed.connect(self.handleItemPressed)

    def addCheckItems(self, all_presets, checked_presets):
        for text in all_presets:
            item = QStandardItem(text)
            item.setFlags((item.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsTristate)            
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            if text in checked_presets:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.model().appendRow(item)

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        item.setFlags((item.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsTristate)
        if item.checkState():
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.updateText()

    def updateText(self):
        self.checked = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState():
                self.checked.append(item.text())
        self.setEditText(", ".join(self.checked))
        
    def getChecked(self):
        return self.checked
