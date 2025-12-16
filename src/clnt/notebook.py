"""
Getz Ronny
notebook
"""

from canvas import *


class Notebook(QtWidgets.QWidget):
    def __init__(self, pages_list, notebook_area):
        """constructor"""
        super().__init__()
        self.notebook_area = notebook_area
        self.pages = QtWidgets.QStackedWidget()
        self.pages_list = []
        if pages_list:
            for page in pages_list:
                self.add_page(DrawingCanvas(**page,
                                            notebook_area=notebook_area))
        self.global_scale_factor = START_SCALE_FACTOR
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.pages)
        if not pages_list:
            self.add_page(None)

    def __dict__(self):
        """convert notebook to dictionary"""
        page_l = []
        for p in self.pages_list:
            page_l.append(p.__dict__())
        notebook_dict = {
            "pages_list": page_l,
        }
        return notebook_dict

    def current_canvas(self):
        """return current canvas"""
        return self.pages.currentWidget()

    def add_page(self, page):
        """add another canvas"""
        if page:
            canvas = page
        else:
            canvas = DrawingCanvas(*CANVAS_SIZE, None,
                                   None, self.notebook_area, None)
        if self.pages_list:
            prev_canvas = self.pages_list[LAST_PAGE_INDEX]
            canvas.scale_factor = prev_canvas.scale_factor
            canvas._update_size()
            if self.notebook_area:
                self.notebook_area.save_notebook()

        self.pages_list.append(canvas)
        self.pages.addWidget(canvas)
        self.pages.setCurrentWidget(canvas)

    def prev_page(self):
        """move to the prev canvas"""
        index = self.pages.currentIndex()
        if index > NO_PAGES:
            self.pages.setCurrentIndex(index - PREV_PAGE)

    def next_page(self):
        """move to the next canvas"""
        index = self.pages.currentIndex()
        if index < len(self.pages_list) + LAST_PAGE_INDEX:
            self.pages.setCurrentIndex(index + NEXT_PAGE)

    def zoom_in(self):
        """change the global scale factor by 1.2 (more)"""
        self.global_scale_factor *= SCALE_CHANGE
        self.global_scale_factor = max(SCALE_MIN,
                                       min(SCALE_MAX,
                                           self.global_scale_factor))
        self.apply_zoom_to_all()

    def zoom_out(self):
        """change the global scale factor by 1.2 (less)"""
        self.global_scale_factor /= SCALE_CHANGE
        self.global_scale_factor = max(SCALE_MIN,
                                       min(SCALE_MAX,
                                           self.global_scale_factor))
        self.apply_zoom_to_all()

    def apply_zoom_to_all(self):
        """change the zoom in all pages"""
        for page in self.pages_list:
            page.scale_factor = self.global_scale_factor
            page._update_size()
            page.update()

    def update_notebook(self, pages_list, notebook_area):
        """update the notebook from the DB"""
        self.notebook_area = notebook_area
        self.delete_old_data()
        if pages_list:
            for page in pages_list:
                canvas = DrawingCanvas(**page, notebook_area=notebook_area)
                self.pages.addWidget(canvas)
                self.pages_list.append(canvas)
        else:
            self.add_page(None)
        self.global_scale_factor = START_SCALE_FACTOR
        self.pages.setCurrentIndex(FIRST_PAGE)

    def delete_old_data(self):
        """delete the old data of the notebook"""
        if hasattr(self, "pages"):
            while self.pages.count():
                widget = self.pages.widget(FIRST_PAGE)
                self.pages.removeWidget(widget)
                widget.deleteLater()
        else:
            self.pages = QtWidgets.QStackedWidget()
            self.main_layout = QtWidgets.QVBoxLayout(self)
            self.main_layout.addWidget(self.pages)
        self.pages_list = []
