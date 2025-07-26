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

        # create eraser size spin box
        self.eraser_size_button = QSpinBox()
        self.eraser_size_button.setRange(*ERASER_RANGE)
        self.eraser_size_button.setValue(ERASER_START_VALUE)
        self.eraser_size_button.setSingleStep(ERASER_STEP)
        self.eraser_size_button.valueChanged.connect(
            self.canvas_widget.change_pen_size)
        self.eraser_size_button.setMinimumWidth(BUTTON_WIDTH)

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
        self.toolbar_features(page_toolbar, central_layout)

        page_toolbar.addWidget(self.blank_button)
        page_toolbar.addWidget(self.lines_button)
        page_toolbar.addWidget(self.grid_button)

        self.page_button = QPushButton(f"page", self)
        self.toolbar_button(self.page_button, PAGE_INDEX)
        self.main_toolbar.addWidget(self.page_button)

        pen_toolbar = QToolBar(f"pen")
        self.toolbar_features(pen_toolbar, central_layout)

        pen_toolbar.addWidget(self.pen_size_button)
        pen_toolbar.addWidget(self.pen_color_button)

        self.pen_button = QPushButton(f"pen", self)
        self.toolbar_button(self.pen_button, PEN_INDEX)
        self.main_toolbar.addWidget(self.pen_button)

        marker_toolbar = QToolBar(f"marker")
        self.toolbar_features(marker_toolbar, central_layout)

        marker_toolbar.addWidget(self.marker_size_button)
        marker_toolbar.addWidget(self.marker_color_button)

        self.marker_button = QPushButton(f"marker", self)
        self.toolbar_button(self.marker_button, MARKER_INDEX)
        self.main_toolbar.addWidget(self.marker_button)

        eraser_toolbar = QToolBar(f"eraser")
        self.toolbar_features(eraser_toolbar, central_layout)

        eraser_toolbar.addWidget(self.eraser_size_button)

        self.eraser_button = QPushButton(f"eraser", self)
        self.toolbar_button(self.eraser_button, ERASER_INDEX)
        self.main_toolbar.addWidget(self.eraser_button)

        clear_button = QPushButton("clear", self)
        self.main_toolbar_button(clear_button, self.canvas_widget.clear_canvas)

        save_button = QPushButton("save", self)
        self.main_toolbar_button(save_button, self.canvas_widget.save_canvas)

        back_button = QPushButton("back", self)
        self.main_toolbar_button(back_button, self.canvas_widget.back)

        scroll_area = CenteredScrollArea(self.canvas_widget)
        central_layout.addWidget(scroll_area)

    def show_sub_toolbar(self, index):
        for i, toolbar in enumerate(self.sub_toolbars):
            if i == index:
                is_visible = toolbar.isVisible()
                toolbar.setVisible(not is_visible)
                self.page_button.setChecked(i == PAGE_INDEX and not is_visible)
                self.pen_button.setChecked(i == PEN_INDEX and not is_visible)
                self.marker_button.setChecked(i == MARKER_INDEX and not is_visible)
                self.eraser_button.setChecked(i == ERASER_INDEX and not is_visible)
                if not is_visible:
                    if i == PAGE_INDEX:
                        self.canvas_widget.set_tool("page")
                    elif i == PEN_INDEX:
                        self.canvas_widget.set_tool("pen")
                        self.canvas_widget.change_pen_color(
                            self.pen_color_button.currentIndex())
                        self.canvas_widget.change_pen_size(
                            self.pen_size_button.value())
                    elif i == MARKER_INDEX:
                        self.canvas_widget.set_tool("marker")
                        self.canvas_widget.change_pen_color(
                            self.marker_color_button.currentIndex())
                        self.canvas_widget.change_pen_size(
                            self.marker_size_button.value())
                    elif i == ERASER_INDEX:
                        self.canvas_widget.set_tool("eraser")
                        self.canvas_widget.change_pen_size(
                            self.eraser_size_button.value())
            else:
                toolbar.setVisible(False)

    def toolbar_button(self, button, index):
        button.setCheckable(True)
        button.setFixedSize(*BUTTON_SIZE)
        button.clicked.connect(
            lambda checked, x=index: self.show_sub_toolbar(x))

    def toolbar_features(self, toolbar, central_layout):
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setVisible(False)
        toolbar.setStyleSheet(SUB_TOOLBAR)
        self.sub_toolbars.append(toolbar)
        central_layout.addWidget(toolbar)

    def main_toolbar_button(self, button, func):
        button.clicked.connect(func)
        button.setFixedSize(*BUTTON_SIZE)
        button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(button)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
