"""
Ronny Getz
Scroll area that centers notebook widget; Ctrl+wheel zooms.
"""
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from style import NO_ENGLE


class CenteredScrollArea(QtWidgets.QScrollArea):

    def __init__(self, notebook_widget):
        """Set resizable widget; center notebook in inner widget."""
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
        """On Ctrl+wheel: zoom in if angleDelta.y() > 0 else zoom out
         else pass to base."""
        if (QApplication.keyboardModifiers() ==
                Qt.KeyboardModifier.ControlModifier):
            if event.angleDelta().y() > NO_ENGLE:
                self.notebook.zoom_in()
            else:
                self.notebook.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
