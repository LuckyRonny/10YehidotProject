"""
Ronny Getz
try gui project
"""

import sys
from PyQt6.QtWidgets import *
from random import choice

texts_answer = [
    "Yes",
    "No",
    "Maybe",
    "Not today",
    "Absolutely"
]


class MainWindow(QMainWindow):
    # subclass of qMainWindow for the main window
    def __init__(self):
        super().__init__()

        # the name of th window
        self.setWindowTitle("Magic 8 Ball")

        # create a label and a line edit
        self.label = QLabel()
        self.enter_text = QLineEdit()

        self.enter_text.textChanged.connect(self.update_label)

        # create buttons
        self.button = QPushButton("enter")
        self.button_clear = QPushButton("clear")

        # connect the function to the clicked signal
        self.button.clicked.connect(self.enter_button_was_clicked)
        self.button_clear.clicked.connect(self.clear_button_was_clicked)

        # set buttons layout
        buttons = QHBoxLayout()
        buttons.addWidget(self.button_clear)
        buttons.addWidget(self.button)

        # set layout
        layout = QVBoxLayout()
        layout.addWidget(self.enter_text)
        layout.addLayout(buttons)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)

        # set the central widget to be the button
        self.setCentralWidget(container)

    def enter_button_was_clicked(self):
        self.label.setText(choice(texts_answer))

    def clear_button_was_clicked(self):
        self.enter_text.clear()
        self.label.clear()

    def update_label(self):
        if self.enter_text.text():
            self.label.setText("thinking...")
        else:
            self.label.clear()


app = QApplication(sys.argv)  # create an app

window = MainWindow()  # create a window
window.show()  # show the window

app.exec()  # start an event loop
