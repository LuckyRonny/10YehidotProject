"""
Ronny Getz
Container widget that centers a child and draws a light blue background.
"""
from PyQt6 import QtGui
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from style import STRETCH

# Background color for canvas container
CANVAS_BG_HEX = "#D3E9FF"


class CanvasContainer(QWidget):
    """Centers a child widget and paints a filled background."""

    def __init__(self, child_widget):
        """Build layout with stretches and child; set background color on paint."""
        super().__init__()
        self.child_widget = child_widget
        layout = QVBoxLayout()
        layout.addStretch(STRETCH)
        h_layout = QHBoxLayout()
        h_layout.addStretch(STRETCH)
        h_layout.addWidget(self.child_widget)
        h_layout.addStretch(STRETCH)
        layout.addLayout(h_layout)
        layout.addStretch(STRETCH)
        self.setLayout(layout)

    def paintEvent(self, event):
        """Fill widget rect with background color."""
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(CANVAS_BG_HEX))
