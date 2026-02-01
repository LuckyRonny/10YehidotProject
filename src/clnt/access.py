"""
ronny getz
Access dialog: per-user permission combo (Admin/Edit/View/No Access).
"""
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from style import *

# Dialog size (width, height)
ACCESS_DIALOG_WIDTH = 350
ACCESS_DIALOG_HEIGHT = 250

ACCESS_DICT = {0: "Admin",
               1: "Edit",
               2: "View",
               3: "No Access"}


class AccessDialog(QDialog):
    def __init__(self, users_with_access, parent=None):
        """Build layout with one row per (username, current_access)
        parent optional."""
        super().__init__(parent)
        self.setWindowTitle("Access Management")
        self.resize(ACCESS_DIALOG_WIDTH, ACCESS_DIALOG_HEIGHT)

        layout = QVBoxLayout(self)

        self.access_levels = ["No Access", "View", "Edit", "Admin"]
        self.user_boxes = {}
        if users_with_access:
            for username, current_access in users_with_access:
                row = QHBoxLayout()
                name_label = QLabel(username)
                combo = QComboBox()
                combo.addItems(self.access_levels)
                access = ACCESS_DICT[current_access]
                if access in self.access_levels:
                    combo.setCurrentText(access)
                else:
                    combo.setCurrentText("No Access")
                row.addWidget(name_label)
                row.addStretch()
                row.addWidget(combo)
                layout.addLayout(row)
                self.user_boxes[username] = combo

        buttons_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_row.addStretch()
        buttons_row.addWidget(save_btn)
        buttons_row.addWidget(cancel_btn)
        layout.addLayout(buttons_row)

    def get_access_data(self):
        """Return dict mapping username to selected access level string."""
        return {
            user: combo.currentText()
            for user, combo in self.user_boxes.items()
        }
