"""
Getz Ronny
Notebook widget: stacked pages (DrawingCanvas), zoom, add/prev/next
 syncs with NotebookArea.
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
        """Build stacked widget and pages from dict or single blank page
         set last_change."""
        super().__init__()
        self.notebook_area = notebook_area
        if notebook_area:
            notebook_area.notebook_widget = self
        self.pages = QtWidgets.QStackedWidget()
        self.pages_list = []
        if pages:
            for page in pages:
                self.add_page(
                    DrawingCanvas(**(pages[page]),
                                  notebook_area=notebook_area),
                    notify_server=False,
                )
        self.global_scale_factor = START_SCALE_FACTOR
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.pages)
        if not pages:
            self.add_page(None)
        self.last_change = last_change

    def __dict__(self):
        """Return dict with pages and last_change for serialization."""
        page_dict = {}
        for p in self.pages_list:
            page_dict[p.id] = p.__dict__()
        notebook_dict = {"pages": page_dict, "last_change": self.last_change}
        return notebook_dict

    def current_canvas(self):
        """return current canvas"""
        return self.pages.currentWidget()

    def add_page(self, page, notify_server=True):
        """Add canvas page (or create new); optionally notify server
         set current widget."""
        if page:
            mycanvas = page
        else:
            mycanvas = DrawingCanvas(
                *CANVAS_SIZE, None, None, self.notebook_area,
                None, self.pages.currentIndex() + NEXT_PAGE)
        if self.pages_list:
            prev_canvas = self.pages_list[LAST_PAGE_INDEX]
            mycanvas.scale_factor = prev_canvas.scale_factor
            mycanvas._update_size()
        self.pages_list.append(mycanvas)
        self.pages.addWidget(mycanvas)
        self.pages.setCurrentWidget(mycanvas)
        if (self.notebook_area and
                hasattr(self.notebook_area, "notebook_widget") and
                self.notebook_area.notebook_widget and notify_server):
            self.notebook_area.add_page(mycanvas.id, mycanvas)
            self.notebook_area.current_page = self.pages.currentIndex()

    def prev_page(self):
        """Switch to previous page if index > 0
         update notebook_area.current_page."""
        index = self.pages.currentIndex()
        if index > NO_PAGES:
            self.pages.setCurrentIndex(index - PREV_PAGE)
            self.notebook_area.current_page = self.pages.currentIndex()

    def next_page(self):
        """Switch to next page if not last
         update notebook_area.current_page."""
        index = self.pages.currentIndex()
        if index < len(self.pages_list) + LAST_PAGE_INDEX:
            self.pages.setCurrentIndex(index + NEXT_PAGE)
            self.notebook_area.current_page = self.pages.currentIndex()

    def zoom_in(self):
        """Increase global scale factor and apply to all pages."""
        self.global_scale_factor *= SCALE_CHANGE
        self.global_scale_factor = max(
            SCALE_MIN, min(SCALE_MAX, self.global_scale_factor)
        )
        self.apply_zoom_to_all()

    def zoom_out(self):
        """Decrease global scale factor and apply to all pages."""
        self.global_scale_factor /= SCALE_CHANGE
        self.global_scale_factor = max(
            SCALE_MIN, min(SCALE_MAX, self.global_scale_factor)
        )
        self.apply_zoom_to_all()

    def apply_zoom_to_all(self):
        """Set each page scale_factor to global and update size/display."""
        for page in self.pages_list:
            page.scale_factor = self.global_scale_factor
            page._update_size()
            page.update()

    def update_notebook(self, ts, type, page, data):
        """Apply server update: ADD_PAGE or dispatch type to matching page
         update last_change."""
        if type == "ADD_PAGE":
            page_id = int(page)
            page_exists = any(p.id == page_id for p in self.pages_list)
            if not page_exists:
                mycanvas = DrawingCanvas(**data,
                                         notebook_area=self.notebook_area)
                if self.pages_list:
                    prev_canvas = self.pages_list[LAST_PAGE_INDEX]
                    mycanvas.scale_factor = prev_canvas.scale_factor
                    mycanvas._update_size()
                self.pages_list.append(mycanvas)
                self.pages.addWidget(mycanvas)
                if self.notebook_area:
                    self.notebook_area.current_page = self.pages.currentIndex()
        else:
            for p in self.pages_list:
                if p.id == int(page):
                    getattr(p, type)(data)
        self.last_change = max(float(self.last_change), float(ts))

    def delete_old_data(self):
        """Remove all page widgets and clear pages_list
         re-add stacked widget to layout."""
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
