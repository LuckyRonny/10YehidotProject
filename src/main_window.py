"""
Ronny Getz
main window
"""

from notebook import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(MAIN_WINDOW)
        self.setMinimumSize(*WINDOW_SIZE)

        # create canvas
        self.notebook_widget = Notebook()
        self.current_page = self.notebook_widget.pages.currentIndex()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(*MARGIN)
        central_widget.setLayout(central_layout)

        # toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.sub_toolbars = []
        self.create_sub_toolbars(central_layout)

        clear_button = QPushButton("clear", self)
        self.main_toolbar_button(clear_button, self.notebook_widget.
                                 pages_list[self.current_page].clear_canvas)

        save_button = QPushButton("save", self)
        self.main_toolbar_button(save_button, self.notebook_widget.
                                 pages_list[self.current_page].save_canvas)

        back_button = QPushButton("back", self)
        self.main_toolbar_button(back_button, self.notebook_widget.
                                 pages_list[self.current_page].back)

        self.btn_prev = QtWidgets.QPushButton("⟨ Prev Page")
        self.btn_next = QtWidgets.QPushButton("Next Page ⟩")
        self.btn_add = QtWidgets.QPushButton("+ Add Page")

        self.btn_prev.clicked.connect(self.notebook_widget.prev_page)
        self.btn_next.clicked.connect(self.notebook_widget.next_page)
        self.btn_add.clicked.connect(self.notebook_widget.add_page)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_next)
        button_layout.addStretch()

        scroll_area = CenteredScrollArea(self.notebook_widget)
        central_layout.addWidget(scroll_area)
        central_layout.addLayout(button_layout)
        central_layout.setStretch(0, 1)

    def show_sub_toolbar(self, index):
        """change between the sub toolbars"""
        for i, toolbar in enumerate(self.sub_toolbars):
            if i == index:
                is_visible = toolbar.isVisible()
                self.set_checked(i, toolbar, is_visible)
                if not is_visible:
                    if i == ToolbarsEnum.PAGE.value:
                        (self.notebook_widget.pages_list[self.current_page]
                         .set_tool("page"))
                    elif i == ToolbarsEnum.SELECT.value:
                        (self.notebook_widget.pages_list[self.current_page]
                         .set_tool("select"))
                        toolbar.setVisible(False)
                    elif i == ToolbarsEnum.PEN.value:
                        (self.notebook_widget.pages_list[self.current_page]
                         .set_tool("pen"))
                        (self.notebook_widget.pages_list[self.current_page]
                         .change_pen_color(
                            self.pen_color_button.currentIndex()))
                        (self.notebook_widget.pages_list[self.current_page]
                         .change_pen_size(
                            self.pen_size_button.value()))
                    elif i == ToolbarsEnum.MARKER.value:
                        (self.notebook_widget.pages_list[self.current_page]
                         .set_tool("marker"))
                        (self.notebook_widget.pages_list[self.current_page]
                         .change_pen_color(
                            self.marker_color_button.currentIndex()))
                        (self.notebook_widget.pages_list[self.current_page]
                         .change_pen_size(self.marker_size_button.value()))
                    elif i == ToolbarsEnum.ERASER.value:
                        (self.notebook_widget.pages_list[self.current_page]
                         .set_tool("eraser"))
                        (self.notebook_widget.pages_list[self.current_page]
                         .change_pen_size(self.eraser_size_button.value()))
            else:
                toolbar.setVisible(False)

    def create_sub_toolbars(self, central_layout):
        """create the sub toolbars and their buttons"""
        # page toolbar and button
        self.page_toolbar = self.create_page_toolbar()
        central_layout.addWidget(self.page_toolbar)
        self.page_button = QPushButton(f"page", self)
        self.toolbar_button(self.page_button, ToolbarsEnum.PAGE.value)
        self.main_toolbar.addWidget(self.page_button)
        # pen toolbar and button
        self.pen_toolbar, self.pen_size_button, self.pen_color_button = (
            self.create_pen_toolbar_and_size_and_color())
        central_layout.addWidget(self.pen_toolbar)
        self.pen_button = QPushButton(f"pen", self)
        self.toolbar_button(self.pen_button, ToolbarsEnum.PEN.value)
        self.main_toolbar.addWidget(self.pen_button)
        # marker toolbar and button
        self.marker_toolbar, self.marker_size_button, self.marker_color_button \
            = (self.create_marker_toolbar_and_size_and_color())
        central_layout.addWidget(self.marker_toolbar)
        self.marker_button = QPushButton(f"marker", self)
        self.toolbar_button(self.marker_button, ToolbarsEnum.MARKER.value)
        self.main_toolbar.addWidget(self.marker_button)
        # eraser toolbar and button
        self.eraser_toolbar, self.eraser_size_button = (
            self.create_eraser_toolbar_and_size())
        central_layout.addWidget(self.eraser_toolbar)
        self.eraser_button = QPushButton(f"eraser", self)
        self.toolbar_button(self.eraser_button, ToolbarsEnum.ERASER.value)
        self.main_toolbar.addWidget(self.eraser_button)
        # select toolbar and button
        self.select_toolbar = self.create_select_toolbar()
        central_layout.addWidget(self.select_toolbar)
        self.select_button = QPushButton(f"select", self)
        self.toolbar_button(self.select_button, ToolbarsEnum.SELECT.value)
        self.main_toolbar.addWidget(self.select_button)

    def set_checked(self, i, toolbar, is_visible):
        """set the right toolbar button checked and visible"""
        toolbar.setVisible(not is_visible)
        self.page_button.setChecked(i == ToolbarsEnum.PAGE.value and
                                    not is_visible)
        self.select_button.setChecked(i == ToolbarsEnum.SELECT.value and
                                      not is_visible)
        self.pen_button.setChecked(i == ToolbarsEnum.PEN.value and
                                   not is_visible)
        self.marker_button.setChecked(i == ToolbarsEnum.MARKER.value and
                                      not is_visible)
        self.eraser_button.setChecked(i == ToolbarsEnum.ERASER.value and
                                      not is_visible)

    def toolbar_button(self, button, index):
        """set features of the button of the sub toolbar buttons"""
        button.setCheckable(True)
        button.setFixedSize(*BUTTON_SIZE)
        button.clicked.connect(
            lambda checked, x=index: self.show_sub_toolbar(x))

    def toolbar_features(self, toolbar):
        """set features of sub toolbars"""
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setVisible(False)
        toolbar.setStyleSheet(SUB_TOOLBAR)
        self.sub_toolbars.append(toolbar)

    def main_toolbar_button(self, button, func):
        """set features of main toolbar"""
        button.clicked.connect(func)
        button.setFixedSize(*BUTTON_SIZE)
        button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(button)

    def create_page_toolbar(self):
        """create page toolbar"""
        blank_button = QPushButton("blank", self)
        blank_button.clicked.connect(self.notebook_widget.pages_list
                                     [self.current_page].blank)
        blank_button.setFixedSize(*BUTTON_SIZE)
        blank_button.setStyleSheet(BUTTON)

        lines_button = QPushButton("lines", self)
        lines_button.clicked.connect(self.notebook_widget.pages_list
                                     [self.current_page].lines)
        lines_button.setFixedSize(*BUTTON_SIZE)
        lines_button.setStyleSheet(BUTTON)

        grid_button = QPushButton("grid", self)
        grid_button.clicked.connect(self.notebook_widget.pages_list
                                    [self.current_page].grid)
        grid_button.setFixedSize(*BUTTON_SIZE)
        grid_button.setStyleSheet(BUTTON)

        page_toolbar = QToolBar(f"page")
        self.toolbar_features(page_toolbar)

        page_toolbar.addWidget(blank_button)
        page_toolbar.addWidget(lines_button)
        page_toolbar.addWidget(grid_button)

        return page_toolbar

    def create_select_toolbar(self):
        """create select toolbar"""
        select_toolbar = QToolBar(f"select")
        self.toolbar_features(select_toolbar)
        return select_toolbar

    def create_pen_toolbar_and_size_and_color(self):
        """create pen toolbar"""
        # create spin box pen size
        pen_size_button = self.create_size_button(PEN_RANGE,
                                                  PEN_START_VALUE,
                                                  PEN_STEP)
        # create combo box pen colors
        pen_color_button = self.create_color_button(COLORS_NAMES)

        pen_toolbar = QToolBar(f"pen")
        self.toolbar_features(pen_toolbar)
        pen_toolbar.addWidget(pen_size_button)
        pen_toolbar.addWidget(pen_color_button)

        return pen_toolbar, pen_size_button, pen_color_button

    def create_marker_toolbar_and_size_and_color(self):
        """create marker toolbar"""
        # create spin box marker size
        marker_size_button = self.create_size_button(MARKER_RANGE,
                                                     MARKER_START_VALUE,
                                                     MARKER_STEP)
        # create combo box marker colors
        marker_color_button = self.create_color_button(MARKER_COLORS_NAMES)

        marker_toolbar = QToolBar(f"marker")
        self.toolbar_features(marker_toolbar)
        marker_toolbar.addWidget(marker_size_button)
        marker_toolbar.addWidget(marker_color_button)

        return marker_toolbar, marker_size_button, marker_color_button

    def create_eraser_toolbar_and_size(self):
        """create eraser toolbar"""
        # create eraser size spin box
        eraser_size_button = self.create_size_button(ERASER_RANGE,
                                                     ERASER_START_VALUE,
                                                     ERASER_STEP)

        eraser_toolbar = QToolBar(f"eraser")
        self.toolbar_features(eraser_toolbar)
        eraser_toolbar.addWidget(eraser_size_button)

        return eraser_toolbar, eraser_size_button

    def create_size_button(self, size_range, start_value, size_step):
        """create size button"""
        size_button = QSpinBox()
        size_button.setRange(*size_range)
        size_button.setValue(start_value)
        size_button.setSingleStep(size_step)
        size_button.valueChanged.connect(
            self.notebook_widget.pages_list[self.current_page].change_pen_size)
        size_button.setMinimumWidth(BUTTON_WIDTH)
        size_button.setMaximumWidth(BUTTON_WIDTH)
        return size_button

    def create_color_button(self, colors):
        """create color button"""
        color_button = QComboBox()
        color_button.addItems(colors)
        color_button.currentIndexChanged.connect(
            self.notebook_widget.pages_list[self.current_page].change_pen_color)
        return color_button


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
