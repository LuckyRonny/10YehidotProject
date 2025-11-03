"""
Ronny Getz
canvas container
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from style import *


class CanvasContainer(QWidget):
    def __init__(self, child_widget):
        """constructor"""
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
        """draw the background"""
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("#D3E9FF"))
