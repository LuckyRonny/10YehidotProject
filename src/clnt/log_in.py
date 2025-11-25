"""
Ronny Getz
window log in
"""

from sign_up import *
from style import *
from main_window import *
from client import *


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """constructor"""
        super().__init__()
        self.setWindowTitle("Sign in")
        self.setStyleSheet(MAIN_WINDOW)
        self.setMinimumSize(*WINDOW_SIZE)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        username_layout = QHBoxLayout()
        self.username_line_edit = self.create_layout(username_layout,
                                                     "Username: ")
        password_layout = QHBoxLayout()
        self.password_line_edit = self.create_layout(password_layout,
                                                     "Password: ")
        error_layout = QHBoxLayout()
        self.error_label = self.create_error_layout(error_layout)
        button_layout = QHBoxLayout()
        self.create_button_layout(button_layout)
        self.create_central_layout(central_layout, username_layout,
                                   password_layout, button_layout, error_layout)
        self.client = Client()

    def create_central_layout(self, central_layout, username_layout,
                              password_layout, button_layout, error_layout):
        """create central layout"""
        central_layout.setContentsMargins(*MARGIN)
        central_layout.addStretch(LOGIN_STRETCH)
        central_layout.addLayout(username_layout)
        central_layout.addLayout(password_layout)
        central_layout.addLayout(error_layout)
        central_layout.addLayout(button_layout)
        central_layout.addStretch(LOGIN_STRETCH)

    def create_layout(self, layout, name):
        """create layout of username and password"""
        label = QLabel(name)
        line_edit = QtWidgets.QLineEdit()
        line_edit.setMaxLength(LINE_EDIT_MAX_LENGTH)
        layout.addStretch(STRETCH)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addStretch(STRETCH)
        return line_edit

    def create_error_layout(self, layout):
        """create error layout"""
        label = QLabel()
        layout.addStretch(STRETCH)
        layout.addWidget(label)
        layout.addStretch(STRETCH)
        return label

    def create_button_layout(self, button_layout):
        """create button layout"""
        button_layout.addStretch(STRETCH)
        login_button = QPushButton("Login")
        login_button.setStyleSheet(LOGIN_BUTTON)
        login_button.setMinimumWidth(BUTTON_WIDTH)
        login_button.setMaximumWidth(BUTTON_WIDTH)
        login_button.setMaximumHeight(BUTTON_HEIGHT)
        login_button.setMinimumHeight(BUTTON_HEIGHT)
        login_button.clicked.connect(self.login_button_clicked)
        button = QPushButton("Sign up")
        button.setStyleSheet(LOGIN_BUTTON)
        button.setMinimumWidth(BUTTON_WIDTH)
        button.setMaximumWidth(BUTTON_WIDTH)
        button.setMaximumHeight(BUTTON_HEIGHT)
        button.setMinimumHeight(BUTTON_HEIGHT)
        button.clicked.connect(self.signin_button_clicked)
        button_layout.addWidget(login_button)
        button_layout.addWidget(button)
        button_layout.addStretch(STRETCH)

    def login_button_clicked(self):
        """if parameters are ok switch main window"""
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        request = "login$" + username + "$" + password + "$1"
        response = self.client.send_command(request).split("!")
        name = response[1]
        response = response[0]
        if response == "ILLEGAL REQUEST" or response == "FALSE":
           self.error_label.setText(
               "Login Failed, one or more of the parameters is incorrect")
        else:
            print(response)
            self.main_window = MainWindow(self.client, response, self, name)
            self.main_window.show()
            self.hide()

    def signin_button_clicked(self):
        """switch to sign up window"""
        self.signup_window = SignupWindow(self)
        self.signup_window.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication([])
    window = LoginWindow()
    window.show()
    app.exec()
