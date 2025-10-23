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
        # central_widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(*MARGIN)
        central_widget.setLayout(central_layout)
        # toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)
        # sub toolbars
        self.sub_toolbars = []
        self.create_sub_toolbars(central_layout)
        # pages button layout
        self.create_buttons()
        button_layout = self.create_buttons_layout()
        # organize widgets
        scroll_area = CenteredScrollArea(self.notebook_widget)
        central_layout.addWidget(scroll_area)
        central_layout.addLayout(button_layout)
        central_layout.setStretch(SCROLL_AREA, SCROLL_STRETCH)

    def show_sub_toolbar(self, index):
        """change between the sub toolbars"""
        for i, toolbar in enumerate(self.sub_toolbars):
            if i == index:
                is_visible = toolbar.isVisible()
                self.set_checked(i, toolbar, is_visible)
                if not is_visible:
                    self.set_tool_and_size_and_color(i, toolbar)
            else:
                toolbar.setVisible(False)

    def set_tool_and_size_and_color(self, i, toolbar):
        """check which toolbar is on and sets the tool, size and color"""
        if i == ToolbarsEnum.PAGE.value:
            (self.set_tool_for_current("page"))
        elif i == ToolbarsEnum.SELECT.value:
            (self.set_tool_for_current("select"))
            toolbar.setVisible(False)
        elif i == ToolbarsEnum.PEN.value:
            self.set_tool_for_current("pen")
            self.set_color_for_current(
                self.pen_color_button.currentIndex())
            self.set_size_for_current(
                self.pen_size_button.value())
        elif i == ToolbarsEnum.MARKER.value:
            self.set_tool_for_current("marker")
            self.set_color_for_current(
                self.marker_color_button.currentIndex())
            self.set_size_for_current(
                self.marker_size_button.value())
        elif i == ToolbarsEnum.ERASER.value:
            self.set_tool_for_current("eraser")
            self.set_size_for_current(
                self.eraser_size_button.value())

    def create_buttons(self):
        """create clear, save, back, prev, next, add page buttons"""
        clear_button = QPushButton("clear", self)
        self.main_toolbar_button(clear_button, self.clear_current_page)
        save_button = QPushButton("save", self)
        self.main_toolbar_button(save_button, self.save_current_page)
        back_button = QPushButton("back", self)
        self.main_toolbar_button(back_button, self.back_current_page)

        self.btn_prev = QtWidgets.QPushButton("⟨ Prev Page")
        self.btn_next = QtWidgets.QPushButton("Next Page ⟩")
        self.btn_add = QtWidgets.QPushButton("+ Add Page")
        self.btn_prev.clicked.connect(self.notebook_widget.prev_page)
        self.btn_next.clicked.connect(self.notebook_widget.next_page)
        self.btn_add.clicked.connect(self.notebook_widget.add_page)

    def create_buttons_layout(self):
        """create button layout"""
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_next)
        button_layout.addStretch()
        return button_layout

    def create_sub_toolbars(self, central_layout):
        """create the sub toolbars and their buttons"""
        # page toolbar and button
        self.create_sub_toolbar_page(central_layout)
        # pen toolbar and button
        self.create_sub_toolbar_pen(central_layout)
        # marker toolbar and button
        self.create_sub_toolbar_marker(central_layout)
        # eraser toolbar and button
        self.create_sub_toolbar_eraser(central_layout)
        # select toolbar and button
        self.create_sub_toolbar_select(central_layout)

    def create_sub_toolbar_page(self, central_layout):
        """create page sub toolbar and button"""
        self.page_toolbar = self.create_page_toolbar()
        central_layout.addWidget(self.page_toolbar)
        self.page_button = QPushButton(f"page", self)
        self.toolbar_button(self.page_button, ToolbarsEnum.PAGE.value)
        self.main_toolbar.addWidget(self.page_button)

    def create_sub_toolbar_pen(self, central_layout):
        """create pen sub toolbar and button"""
        self.pen_toolbar, self.pen_size_button, self.pen_color_button = (
            self.create_pen_toolbar_and_size_and_color())
        central_layout.addWidget(self.pen_toolbar)
        self.pen_button = QPushButton(f"pen", self)
        self.toolbar_button(self.pen_button, ToolbarsEnum.PEN.value)
        self.main_toolbar.addWidget(self.pen_button)

    def create_sub_toolbar_marker(self, central_layout):
        """create marker sub toolbar and button"""
        self.marker_toolbar, self.marker_size_button, self.marker_color_button\
            = (self.create_marker_toolbar_and_size_and_color())
        central_layout.addWidget(self.marker_toolbar)
        self.marker_button = QPushButton(f"marker", self)
        self.toolbar_button(self.marker_button, ToolbarsEnum.MARKER.value)
        self.main_toolbar.addWidget(self.marker_button)

    def create_sub_toolbar_eraser(self, central_layout):
        """create eraser sub toolbar and button"""
        self.eraser_toolbar, self.eraser_size_button = (
            self.create_eraser_toolbar_and_size())
        central_layout.addWidget(self.eraser_toolbar)
        self.eraser_button = QPushButton(f"eraser", self)
        self.toolbar_button(self.eraser_button, ToolbarsEnum.ERASER.value)
        self.main_toolbar.addWidget(self.eraser_button)

    def create_sub_toolbar_select(self, central_layout):
        """create select sub toolbar and button"""
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

    def clear_current_page(self):
        """calls the clear_canvas func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            canvas.clear_canvas()

    def save_current_page(self):
        """calls the save func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            canvas.save_canvas()

    def back_current_page(self):
        """calls the back func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            canvas.back()

    def set_tool_for_current(self, tool_name):
        """calls the set_tool func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            canvas.set_tool(tool_name)

    def set_size_for_current(self, size):
        """calls the change_pen_size func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            canvas.change_pen_size(size)

    def set_color_for_current(self, color):
        """calls the change_pen_color func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            canvas.change_pen_color(color)

    def set_background_for_current(self, background):
        """calls the right background func on current page"""
        canvas = self.notebook_widget.current_canvas()
        if canvas:
            if background == "grid":
                canvas.grid()
            elif background == "lines":
                canvas.lines()
            else:
                canvas.blank()

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

    def create_page_buttons(self):
        """create blank, lines and grid buttons"""
        blank_button = QPushButton("blank", self)
        blank_button.clicked.connect(lambda:
                                     self.set_background_for_current("blank"))
        blank_button.setFixedSize(*BUTTON_SIZE)
        blank_button.setStyleSheet(BUTTON)
        lines_button = QPushButton("lines", self)
        lines_button.clicked.connect(lambda:
                                     self.set_background_for_current("lines"))
        lines_button.setFixedSize(*BUTTON_SIZE)
        lines_button.setStyleSheet(BUTTON)
        grid_button = QPushButton("grid", self)
        grid_button.clicked.connect(lambda:
                                    self.set_background_for_current("grid"))
        grid_button.setFixedSize(*BUTTON_SIZE)
        grid_button.setStyleSheet(BUTTON)
        return blank_button, lines_button, grid_button

    def create_page_toolbar(self):
        """create page toolbar"""
        blank_button, lines_button, grid_button = self.create_page_buttons()

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
            self.set_size_for_current)
        size_button.setMinimumWidth(BUTTON_WIDTH)
        size_button.setMaximumWidth(BUTTON_WIDTH)
        return size_button

    def create_color_button(self, colors):
        """create color button"""
        color_button = QComboBox()
        color_button.addItems(colors)
        color_button.currentIndexChanged.connect(
            self.set_color_for_current)
        return color_button


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
