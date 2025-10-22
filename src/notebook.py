"""
Getz Ronny
notebook
"""

from canvas import *


class Notebook(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pages = QtWidgets.QStackedWidget()
        self.pages_list = []
        self.global_scale_factor = 1.0

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.pages)

        self.add_page()

    def current_canvas(self):
        """"""
        return self.pages.currentWidget()

    def add_page(self):
        canvas = DrawingCanvas(*CANVAS_SIZE)
        if self.pages_list:
            prev_canvas = self.pages_list[-1]
            canvas.scale_factor = prev_canvas.scale_factor
            canvas._update_size()

        self.pages_list.append(canvas)
        self.pages.addWidget(canvas)
        self.pages.setCurrentWidget(canvas)

    def prev_page(self):
        index = self.pages.currentIndex()
        if index > 0:
            self.pages.setCurrentIndex(index - 1)

    def next_page(self):
        index = self.pages.currentIndex()
        if index < len(self.pages_list) - 1:
            self.pages.setCurrentIndex(index + 1)

    def zoom_in(self):
        self.global_scale_factor *= SCALE_CHANGE
        self.global_scale_factor = max(SCALE_MIN,
                                       min(SCALE_MAX, self.global_scale_factor))
        self.apply_zoom_to_all()

    def zoom_out(self):
        self.global_scale_factor /= SCALE_CHANGE
        self.global_scale_factor = max(SCALE_MIN,
                                       min(SCALE_MAX, self.global_scale_factor))
        self.apply_zoom_to_all()

    def apply_zoom_to_all(self):
        """"""
        for page in self.pages_list:
            page.scale_factor = self.global_scale_factor
            page._update_size()
            page.update()
