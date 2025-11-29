"""
Ronny Getz
main window
"""
from PyQt6.QtGui import QIcon
from flow_layout import *
from notebook_area import *
import ast


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, client, id, login_window, name):
        """constructor"""
        super().__init__()
        self.setWindowTitle("")
        self.setStyleSheet(MAIN_WINDOW)
        self.setMinimumSize(*WINDOW_SIZE)
        self.login_window = login_window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # main layout attached to central_widget (important)
        self.layout = QVBoxLayout(self.central_widget)
        self.create_toolbar(name)
        # create the floating box
        self.create_add_frame()
        self.client = client
        # FlowLayout: must be wrapped in a QWidget before adding to main layout
        self.create_flow_layout()
        self.id = id
        self.load_notebooks_for_user(self.id)

    def create_flow_layout(self):
        """creates flow layout"""
        self.notebooks_layout = FlowLayout()
        container_flow_layout = QWidget(self.central_widget)
        container_flow_layout.setLayout(self.notebooks_layout)
        self.layout.addWidget(container_flow_layout)

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
        button.setIconSize(QSize(*ADD_BUTTON_SIZE))
        button.setStyleSheet(ADD_NOTEBOOK_BUTTON)
        button.setMinimumWidth(ADD_NOTEBOOK_SIZE)
        button.setMaximumWidth(ADD_NOTEBOOK_SIZE)
        button.setMaximumHeight(ADD_NOTEBOOK_SIZE)
        button.setMinimumHeight(ADD_NOTEBOOK_SIZE)
        button.clicked.connect(self.create_new_notebook_frame)
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

    def create_add_frame(self):
        """create floating frame parented to central_widget so, it floats"""
        self.create_box()
        box_layout = QVBoxLayout(self.box)
        label = QLabel("notebook name:")
        line_edit = QtWidgets.QLineEdit()
        line_edit.setMaxLength(LINE_EDIT_MAX_LENGTH)
        box_layout.addStretch(STRETCH)
        box_layout.addWidget(label)
        box_layout.addWidget(line_edit)
        box_layout.addStretch(STRETCH)
        button = self.create_button(line_edit)
        box_layout.addWidget(button)
        self.box.setVisible(False)
        self.box_margin_right = BOX_MARGIN_RIGHT
        self.box_margin_top = BOX_MARGIN_LEFT
        self.reposition_box()

    def create_box(self):
        """creates box"""
        self.box = QFrame(self.central_widget)
        self.box.setStyleSheet(ADD_NOTEBOOK_FRAME)
        self.box.setFrameShape(QFrame.Shape.Box)
        self.box.setLineWidth(BOX_LINE_SIZE)
        self.box.setFixedSize(*BOX_SIZE)

    def create_button(self, line_edit):
        """creates create button"""
        button = QPushButton("create")
        button.setStyleSheet(LOGIN_BUTTON)
        button.setMinimumWidth(BUTTON_WIDTH)
        button.setMaximumWidth(BUTTON_WIDTH)
        button.setMaximumHeight(BUTTON_HEIGHT)
        button.setMinimumHeight(BUTTON_HEIGHT)
        button.clicked.connect(lambda: self.create_new_notebook(
            self.id, line_edit.text()))
        return button

    def create_new_notebook_frame(self):
        """toggle floating box visibility"""
        is_visible = self.box.isVisible()
        self.box.setVisible(not is_visible)
        if not is_visible:
            self.box.raise_()  # ensure it's above the flow widgets
            self.reposition_box()

    def create_new_notebook(self, id, notebook_name):
        """creates a new notebook"""
        notebook = Notebook(None, None)
        notebook = repr(notebook.__dict__())
        command = ("add_notebook_to_db$" + id + "$" + notebook_name +
                   "$" + notebook + "$3")
        if self.client.send_command(command) == "ok":
            self.box.setVisible(False)
            button = self.create_notebook_button(notebook_name)
            self.notebooks_buttons.append(button)
            button.clicked.connect(lambda: self.open_notebook(notebook_name))
            self.notebooks_layout.addWidget(button)

    def resizeEvent(self, event):
        """when window resizes, reposition the floating box to top-right"""
        super().resizeEvent(event)
        self.reposition_box()

    def reposition_box(self):
        """helper to position the box at top-right inside central_widget"""
        if not hasattr(self, "box"):
            return
        w = self.central_widget.width()
        x = max(BOX_MIN_MARGIN, w - self.box.width() - self.box_margin_right)
        y = self.box_margin_top
        self.box.move(x, y)
        # ensure box is above everything
        self.box.raise_()

    def create_notebook_button(self, name):
        """create the notebook button"""
        button = QPushButton(name)
        button.setMinimumSize(*NOTEBOOK_BUTTON_SIZE)
        button.setMaximumSize(*NOTEBOOK_BUTTON_SIZE)
        return button

    def load_notebooks_for_user(self, user_id):
        """add the notebooks of a client to the flow layout"""
        command = "clients_notebooks$" + user_id + "$3"
        notebooks = (self.client.send_command(command)).split("!")
        self.notebooks_buttons = []
        for name in notebooks:
            if not name == "":
                button = self.create_notebook_button(name)
                self.notebooks_buttons.append(button)
                button.clicked.connect(lambda checked, n=name:
                                       self.open_notebook(n))
                self.notebooks_layout.addWidget(button)

    def open_notebook(self, name):
        """get the notebook from the server and opens it"""
        command = "get_notebook$" + name + "$2"
        notebook = ast.literal_eval(self.client.send_command(command))
        self.notebook_area = NotebookArea(self, self.id, self.client,
                                          notebook, name)
        self.notebook_area.show()
        self.hide()
