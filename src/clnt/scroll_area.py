"""
Ronny Getz
scroll area
"""

from style import *
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


class CenteredScrollArea(QtWidgets.QScrollArea):
    def __init__(self, notebook_widget):
        """constructor"""
        super().__init__()

        self.setWidgetResizable(True)
        self.notebook = notebook_widget

        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_widget)
        center_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        center_layout.addWidget(notebook_widget,
                                alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.setWidget(center_widget)

    def wheelEvent(self, event):
        """Zoom in/out when scrolling with Ctrl"""
        if (QApplication.keyboardModifiers() ==
                Qt.KeyboardModifier.ControlModifier):
            if event.angleDelta().y() > NO_ENGLE:
                self.notebook.zoom_in()
            else:
                self.notebook.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
