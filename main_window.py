"""

"""
from canvas import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(MAIN_WINDOW)
        self.setMinimumSize(*WINDOW_SIZE)

        # create pixmap
        self.canvas_widget = DrawingCanvas(*CANVAS_SIZE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(*MARGIN)
        central_widget.setLayout(central_layout)

        # create pen size spin box
        self.pen_size_button = QSpinBox()
        self.pen_size_button.setRange(*PEN_RANGE)
        self.pen_size_button.setValue(PEN_START_VALUE)
        self.pen_size_button.setSingleStep(PEN_STEP)
        self.pen_size_button.valueChanged.connect(
            self.canvas_widget.change_pen_size)
        self.pen_size_button.setMinimumWidth(BUTTON_WIDTH)

        # create combo box pen colors
        self.pen_color_button = QComboBox()
        self.pen_color_button.addItems(COLORS_NAMES)
        self.pen_color_button.currentIndexChanged.connect(
            self.canvas_widget.change_pen_color)

        # create marker size spin box
        self.marker_size_button = QSpinBox()
        self.marker_size_button.setRange(*MARKER_RANGE)
        self.marker_size_button.setValue(MARKER_START_VALUE)
        self.marker_size_button.setSingleStep(MARKER_STEP)
        self.marker_size_button.setMinimumWidth(BUTTON_WIDTH)
        self.marker_size_button.valueChanged.connect(
            self.canvas_widget.change_pen_size)

        self.marker_color_button = QComboBox()
        self.marker_color_button.addItems(MARKER_COLORS_NAMES)
        self.marker_color_button.currentIndexChanged.connect(
            self.canvas_widget.change_pen_color)

        # toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.blank_button = QPushButton("blank", self)
        self.blank_button.clicked.connect(self.canvas_widget.blank)
        self.blank_button.setFixedSize(*BUTTON_SIZE)
        self.blank_button.setStyleSheet(BUTTON)

        self.lines_button = QPushButton("lines", self)
        self.lines_button.clicked.connect(self.canvas_widget.lines)
        self.lines_button.setFixedSize(*BUTTON_SIZE)
        self.lines_button.setStyleSheet(BUTTON)

        self.grid_button = QPushButton("grid", self)
        self.grid_button.clicked.connect(self.canvas_widget.grid)
        self.grid_button.setFixedSize(*BUTTON_SIZE)
        self.grid_button.setStyleSheet(BUTTON)

        self.sub_toolbars = []

        page_toolbar = QToolBar(f"page")
        page_toolbar.setMovable(False)
        page_toolbar.setFloatable(False)
        page_toolbar.setVisible(False)
        page_toolbar.setStyleSheet(SUB_TOOLBAR)

        page_toolbar.addWidget(self.blank_button)
        page_toolbar.addWidget(self.lines_button)
        page_toolbar.addWidget(self.grid_button)

        self.sub_toolbars.append(page_toolbar)
        central_layout.addWidget(page_toolbar)

        self.page_button = QPushButton(f"page", self)
        self.page_button.setCheckable(True)
        self.page_button.setFixedSize(*BUTTON_SIZE)
        self.page_button.clicked.connect(
            lambda checked, x=0: self.show_sub_toolbar(x))
        self.main_toolbar.addWidget(self.page_button)

        pen_toolbar = QToolBar(f"pen")
        pen_toolbar.setMovable(False)
        pen_toolbar.setFloatable(False)
        pen_toolbar.setVisible(False)
        pen_toolbar.setStyleSheet(SUB_TOOLBAR)

        pen_toolbar.addWidget(self.pen_size_button)
        pen_toolbar.addWidget(self.pen_color_button)

        self.sub_toolbars.append(pen_toolbar)
        central_layout.addWidget(pen_toolbar)

        self.pen_button = QPushButton(f"pen", self)
        self.pen_button.setCheckable(True)
        self.pen_button.setFixedSize(*BUTTON_SIZE)
        self.pen_button.clicked.connect(
            lambda checked, x=1: self.show_sub_toolbar(x))
        self.main_toolbar.addWidget(self.pen_button)

        marker_toolbar = QToolBar(f"marker")
        marker_toolbar.setMovable(False)
        marker_toolbar.setFloatable(False)
        marker_toolbar.setVisible(False)
        marker_toolbar.setStyleSheet(SUB_TOOLBAR)

        marker_toolbar.addWidget(self.marker_size_button)
        marker_toolbar.addWidget(self.marker_color_button)

        self.sub_toolbars.append(marker_toolbar)
        central_layout.addWidget(marker_toolbar)

        self.marker_button = QPushButton(f"marker", self)
        self.marker_button.setCheckable(True)
        self.marker_button.setFixedSize(*BUTTON_SIZE)
        self.marker_button.clicked.connect(
            lambda checked, x=2: self.show_sub_toolbar(x))
        self.main_toolbar.addWidget(self.marker_button)

        clear_button = QPushButton("clear", self)
        clear_button.clicked.connect(self.canvas_widget.clear_canvas)
        clear_button.setFixedSize(*BUTTON_SIZE)
        clear_button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(clear_button)

        save_button = QPushButton("save", self)
        saved_massage = QMessageBox()
        save_button.clicked.connect(
            lambda msg=saved_massage: self.canvas_widget.save_canvas(msg))
        save_button.setFixedSize(*BUTTON_SIZE)
        save_button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(save_button)

        back_button = QPushButton("back", self)
        back_button.clicked.connect(self.canvas_widget.back)
        back_button.setFixedSize(*BUTTON_SIZE)
        back_button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(back_button)

        scroll_area = CenteredScrollArea(self.canvas_widget)
        central_layout.addWidget(scroll_area)

    def show_sub_toolbar(self, index):
        for i, toolbar in enumerate(self.sub_toolbars):
            if i == index:
                is_visible = toolbar.isVisible()
                toolbar.setVisible(not is_visible)
                self.page_button.setChecked(i == 0 and not is_visible)
                self.pen_button.setChecked(i == 1 and not is_visible)
                self.marker_button.setChecked(i == 2 and not is_visible)
                if not is_visible:
                    if i == 0:
                        self.canvas_widget.set_tool("page")

                    elif i == 1:
                        self.canvas_widget.set_tool("pen")
                        self.canvas_widget.change_pen_color(
                            self.pen_color_button.currentIndex())
                        self.canvas_widget.change_pen_size(
                            self.pen_size_button.value())
                    elif i == 2:
                        self.canvas_widget.set_tool("marker")
                        self.canvas_widget.change_pen_color(
                            self.marker_color_button.currentIndex())
                        self.canvas_widget.change_pen_size(
                            self.marker_size_button.value())
            else:
                toolbar.setVisible(False)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
