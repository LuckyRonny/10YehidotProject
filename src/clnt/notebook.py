"""
Getz Ronny
notebook
"""

from PyQt6 import QtWidgets

from canvas import DrawingCanvas
from style import (
    CANVAS_SIZE,
    FIRST_PAGE,
    LAST_PAGE_INDEX,
    NEXT_PAGE,
    NO_PAGES,
    PREV_PAGE,
    SCALE_CHANGE,
    SCALE_MAX,
    SCALE_MIN,
    START_SCALE_FACTOR,
)


class Notebook(QtWidgets.QWidget):
    def __init__(self, pages, last_change, notebook_area):
        """constructor"""
        super().__init__()
        self.notebook_area = notebook_area
        # Set notebook_widget reference early so add_page can access it during init
        if notebook_area:
            notebook_area.notebook_widget = self
        self.pages = QtWidgets.QStackedWidget()
        self.pages_list = []
        if pages:
            for page in pages:
                self.add_page(
                    DrawingCanvas(**(pages[page]), notebook_area=notebook_area),
                    notify_server=False,
                )
        self.global_scale_factor = START_SCALE_FACTOR
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.pages)
        if not pages:
            self.add_page(None)
        self.last_change = last_change

    def __dict__(self):
        """convert notebook to dictionary"""
        page_dict = {}
        for p in self.pages_list:
            page_dict[p.id] = p.__dict__()
        notebook_dict = {"pages": page_dict, "last_change": self.last_change}
        return notebook_dict

    def current_canvas(self):
        """return current canvas"""
        return self.pages.currentWidget()

    def add_page(self, page, notify_server=True):
        """add another canvas
        :param page: The canvas page to add, or None to create a new one
        :param notify_server: Whether to notify the server about the new page,
        fault: True. Set to False when handling server updates.
        """
        if page:
            mycanvas = page
        else:
            mycanvas = DrawingCanvas(
                *CANVAS_SIZE,
                None,
                None,
                self.notebook_area,
                None,
                self.pages.currentIndex() + NEXT_PAGE,
            )
        if self.pages_list:
            prev_canvas = self.pages_list[LAST_PAGE_INDEX]
            mycanvas.scale_factor = prev_canvas.scale_factor
            mycanvas._update_size()
        self.pages_list.append(mycanvas)
        self.pages.addWidget(mycanvas)
        self.pages.setCurrentWidget(mycanvas)
        if (
            self.notebook_area
            and hasattr(self.notebook_area, "notebook_widget")
            and self.notebook_area.notebook_widget
            and notify_server
        ):
            self.notebook_area.add_page(mycanvas.id, mycanvas)
            self.notebook_area.current_page = self.pages.currentIndex()

    def prev_page(self):
        """move to the prev canvas"""
        index = self.pages.currentIndex()
        if index > NO_PAGES:
            self.pages.setCurrentIndex(index - PREV_PAGE)
            self.notebook_area.current_page = self.pages.currentIndex()

    def next_page(self):
        """move to the next canvas"""
        index = self.pages.currentIndex()
        if index < len(self.pages_list) + LAST_PAGE_INDEX:
            self.pages.setCurrentIndex(index + NEXT_PAGE)
            self.notebook_area.current_page = self.pages.currentIndex()

    def zoom_in(self):
        """change the global scale factor by 1.2 (more)"""
        self.global_scale_factor *= SCALE_CHANGE
        self.global_scale_factor = max(
            SCALE_MIN, min(SCALE_MAX, self.global_scale_factor)
        )
        self.apply_zoom_to_all()

    def zoom_out(self):
        """change the global scale factor by 1.2 (less)"""
        self.global_scale_factor /= SCALE_CHANGE
        self.global_scale_factor = max(
            SCALE_MIN, min(SCALE_MAX, self.global_scale_factor)
        )
        self.apply_zoom_to_all()

    def apply_zoom_to_all(self):
        """change the zoom in all pages"""
        for page in self.pages_list:
            page.scale_factor = self.global_scale_factor
            page._update_size()
            page.update()

    def update_notebook(self, ts, type, page, data):
        """update the notebook from the DB"""
        if type == "ADD_PAGE":
            # Check if page already exists to avoid duplicates
            page_id = int(page)
            page_exists = any(p.id == page_id for p in self.pages_list)
            if not page_exists:
                # Create canvas from server data without notifying server
                mycanvas = DrawingCanvas(**data, notebook_area=self.notebook_area)
                if self.pages_list:
                    prev_canvas = self.pages_list[LAST_PAGE_INDEX]
                    mycanvas.scale_factor = prev_canvas.scale_factor
                    mycanvas._update_size()
                self.pages_list.append(mycanvas)
                self.pages.addWidget(mycanvas)
                # Don't call add_page with notify_server=True to avoid loop
                if self.notebook_area:
                    self.notebook_area.current_page = self.pages.currentIndex()
        else:
            for p in self.pages_list:
                if p.id == int(page):
                    getattr(p, type)(data)
        # Use maximum to ensure we don't go backwards in time
        # This prevents missing updates when local changes have newer timestamps
        self.last_change = max(float(self.last_change), float(ts))

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
