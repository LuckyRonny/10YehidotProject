"""
ronny getz
access
"""
from PyQt6.QtWidgets import (QLabel, QComboBox, QPushButton,
                             QVBoxLayout, QHBoxLayout, QDialog)
from PyQt6.QtGui import QAction

ACCESS_DICT = {0: "Admin",
               1: "Edit",
               2: "View",
               3: "No Access"}


class AccessDialog(QDialog):
    def __init__(self, users_with_access, parent=None):
        """
        users_with_access: list of tuples [(username, current_access), ...]
        """
        super().__init__(parent)
        self.setWindowTitle("Access Management")
        self.resize(350, 250)

        layout = QVBoxLayout(self)

        self.access_levels = ["No Access", "View", "Edit", "Admin"]
        self.user_boxes = {}

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
        return {
            user: combo.currentText()
            for user, combo in self.user_boxes.items()
        }
