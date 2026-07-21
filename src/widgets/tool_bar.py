"""
Small reusable top toolbar widget for the Airfoil Designer.
Provides easy API to add buttons with optional icons and keyboard shortcuts.
"""

from PyQt6.QtWidgets import QToolBar, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence


class ToolBar(QToolBar):
    """A QToolBar placed in the QMainWindow top area under the menu bar.

    Use add_tool_button(text, icon_path=None, shortcut=None, callback=None)
    to add actions (which are presented as toolbar buttons) with optional keyboard shortcuts.
    """

    def __init__(self, program=None, project=None, parent=None, 
                 new_file_callback=None, open_file_callback=None, save_file_callback=None, edit_descr_callback=None,
                 height=75):
        super().__init__(parent)
        self.DAEDALUS = program
        self.PROJECT = project
        self.setFixedHeight(height)
        self.setMovable(True)
        self.setFloatable(True)
        # Show text beside icons so labels are visible
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32,32))

        self.add_tool_button("New Project", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/NewFile.svg", shortcut="Ctrl+N", callback=new_file_callback)
        self.add_tool_button("Open Project", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/OpenFile.svg", shortcut="Ctrl+O", callback=open_file_callback)
        self.add_tool_button("Save Project", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/SaveProject.svg", shortcut="Ctrl+S", callback=save_file_callback)
        self.add_tool_button("Edit Description", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/Editdescription.svg", shortcut="Ctrl+E", callback=edit_descr_callback)

        def _rgb(c):
            if isinstance(c, (tuple, list)):
                return ",".join(str(x) for x in c)
            return c

    def add_tool_button(self, text, icon_path=None, shortcut=None, callback=None):
        """Add an action to the toolbar.

        - text: label shown on the tool button
        - icon_path: optional path for icon
        - shortcut: optional string understood by QKeySequence (e.g., 'Ctrl+1')
        - callback: callable to connect to action triggered

        Returns the created QAction.
        """
        action = QAction(QIcon(icon_path) if icon_path else QIcon(), text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if callback:
            action.triggered.connect(callback)
        self.addAction(action)
        # Keep accessibility tooltip showing shortcut
        if shortcut:
            action.setToolTip(f"{text} ({shortcut})")
        return action

class AirfoilToolBar(QToolBar):
    """A QToolBar placed in the QMainWindow top area under the menu bar.

    Use add_tool_button(text, icon_path=None, shortcut=None, callback=None)
    to add actions (which are presented as toolbar buttons) with optional keyboard shortcuts.
    """

    def __init__(self, program=None, project=None, parent=None, 
                 new_airfoil_callback=None, append_airfoil_callback=None, delete_airfoil_callback=None, 
                 flip_airfoil_callback=None, save_airfoil_callback=None, height=75):
        super().__init__(parent)
        self.DAEDALUS = program
        self.PROJECT = project
        self.setFixedHeight(height)
        self.setMovable(True)
        self.setFloatable(True)
        # Show text beside icons so labels are visible
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32,32))
        
        # Add tool buttons wired to the provided callbacks
        self.add_tool_button("New Airfoil",    icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AddAirfoil.svg",    shortcut="Shift+N", callback=new_airfoil_callback)
        self.add_tool_button("Append Airfoil", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AppendAirfoil.svg", shortcut="Shift+A", callback=append_airfoil_callback)
        self.add_tool_button("Delete Airfoil", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/DeleteAirfoil.svg", shortcut="Shift+X", callback=delete_airfoil_callback)
        self.add_tool_button("Flip Airfoil",   icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/FlipAirfoil.svg",   shortcut="Shift+F", callback=flip_airfoil_callback)
        self.add_tool_button("Save Airfoil",   icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/SaveAirfoil.svg",   shortcut="Shift+S", callback=save_airfoil_callback)

        def _rgb(c):
            if isinstance(c, (tuple, list)):
                return ",".join(str(x) for x in c)
            return c

    def add_tool_button(self, text, icon_path=None, shortcut=None, callback=None):
        """Add an action to the toolbar.

        - text: label shown on the tool button
        - icon_path: optional path for icon
        - shortcut: optional string understood by QKeySequence (e.g., 'Ctrl+1')
        - callback: callable to connect to action triggered

        Returns the created QAction.
        """
        action = QAction(QIcon(icon_path) if icon_path else QIcon(), text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if callback:
            action.triggered.connect(callback)
        self.addAction(action)
        # Keep accessibility tooltip showing shortcut
        if shortcut:
            action.setToolTip(f"{text} ({shortcut})")
        return action

class WingToolBar(QToolBar):
    """A QToolBar placed in the QMainWindow top area under the menu bar.

    Use add_tool_button(text, icon_path=None, shortcut=None, callback=None)
    to add actions (which are presented as toolbar buttons) with optional keyboard shortcuts.
    """

    def __init__(self, program=None, project=None, parent=None, 
                 add_comp_callback=None, del_comp_callback=None, 
                 add_wing_callback=None, del_wing_callback=None,
                 add_segm_callback=None, del_segm_callback=None,
                 height=75):
        super().__init__(parent)
        self.DAEDALUS = program
        self.PROJECT = project
        self.setFixedHeight(height)
        self.setMovable(True)
        self.setFloatable(True)
        # Show text beside icons so labels are visible
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32,32))
        
        # Add tool buttons wired to the provided callbacks
        self.add_tool_button("Add Component",    icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AddComponent.svg",    shortcut="Shift+C", callback=add_comp_callback)
        self.add_tool_button("Delete Component", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/DeleteComponent.svg", shortcut="Shift+X", callback=del_comp_callback)
        self.add_tool_button("Add Wing",         icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AddWing.svg",         shortcut="Shift+W", callback=add_wing_callback)
        self.add_tool_button("Delete Wing",      icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/DeleteWing.svg",      shortcut="Shift+X", callback=del_wing_callback)
        self.add_tool_button("Add Segment",      icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AddSegment.svg",      shortcut="Shift+S", callback=add_segm_callback)
        self.add_tool_button("Delete Segment",   icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/DeleteSegment.svg",   shortcut="Shift+X", callback=del_segm_callback)

        def _rgb(c):
            if isinstance(c, (tuple, list)):
                return ",".join(str(x) for x in c)
            return c

    def add_tool_button(self, text, icon_path=None, shortcut=None, callback=None):
        """Add an action to the toolbar.

        - text: label shown on the tool button
        - icon_path: optional path for icon
        - shortcut: optional string understood by QKeySequence (e.g., 'Ctrl+1')
        - callback: callable to connect to action triggered

        Returns the created QAction.
        """
        action = QAction(QIcon(icon_path) if icon_path else QIcon(), text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if callback:
            action.triggered.connect(callback)
        self.addAction(action)
        # Keep accessibility tooltip showing shortcut
        if shortcut:
            action.setToolTip(f"{text} ({shortcut})")
        return action