'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

'''

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, qApp

class Table(QtWidgets.QTableWidget):
    """
    Context menu for the table.
    """
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        index = self.indexAt(event.pos())
        someAction = menu.addAction("Some Action")
        if index.isValid():
            someAction.setText('Selected item: "{}"'.format(index.data()))
        else:
            someAction.setText('No selection')
            someAction.setEnabled(False)
        anotherAction = menu.addAction("Do something")

        res = menu.exec_(event.globalPos())
        if res == someAction:
            print('first action triggered')

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        self.table = Table(10,4)
        layout.addWidget(self.table)
        layout.addStretch()

        central.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        central.customContextMenuRequested.connect(self.emptySpaceMenu)

    def emptySpaceMenu(self):
        menu = QtWidgets.QMenu()
        menu.addAction('You clicked on the empty space')
        menu.exec_(QtGui.QCursor.pos())

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
        
        