"""
Ronny Getz
main window
"""
from PyQt6.QtGui import QIcon
from flow_layout import *
from notebook_area import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, client, name, login_window):
        """constructor"""
        super().__init__()
        self.setWindowTitle("")
        self.setStyleSheet(MAIN_WINDOW)
        self.setMinimumSize(*WINDOW_SIZE)
        self.login_window = login_window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.create_toolbar(name)
        self.client = client
        self.notebooks_layout = FlowLayout()


    def create_toolbar(self, name):
        """create toolbar"""
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)
        label = QLabel(name)
        label.setStyleSheet(NAME_LABEL)
        add_button = self.create_add_button()
        self.main_toolbar.addWidget(label)
        self.create_log_out_button()
        spacer = QWidget()
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred
        )
        spacer.setStyleSheet("""
                        background-color: #1B0BA6;
                        """)
        self.main_toolbar.addWidget(spacer)
        self.main_toolbar.addWidget(add_button)

    def create_add_button(self):
        """create add button"""
        button = QPushButton("")
        button.setIcon(QIcon("plus_pic.png"))
        button.setIconSize(QSize(40, 40))
        button.setStyleSheet(ADD_NOTEBOOK_BUTTON)
        button.setMinimumWidth(ADD_NOTEBOOK_SIZE)
        button.setMaximumWidth(ADD_NOTEBOOK_SIZE)
        button.setMaximumHeight(ADD_NOTEBOOK_SIZE)
        button.setMinimumHeight(ADD_NOTEBOOK_SIZE)
        return button

    def create_log_out_button(self):
        """create log out button"""
        button = QPushButton("log out")
        button.setStyleSheet(LOGOUT_BUTTON)
        button.setMinimumWidth(BUTTON_WIDTH)
        button.setMaximumWidth(BUTTON_WIDTH)
        button.setMaximumHeight(ADD_NOTEBOOK_SIZE)
        button.setMinimumHeight(ADD_NOTEBOOK_SIZE)
        button.clicked.connect(self.log_out)
        self.main_toolbar.addWidget(button)

    def log_out(self):
        """log out"""
        self.login_window.username_line_edit.clear()
        self.login_window.password_line_edit.clear()
        self.login_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow(Client(), 0)
    window.show()
    app.exec()
