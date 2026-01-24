"""
Getz Ronny
notebook
"""

from PyQt6 import QtWidgets

import canvas
from canvas import DrawingCanvas
from style import *


class Notebook(QtWidgets.QWidget):
    def __init__(self, pages, last_change, notebook_area):
        """constructor"""
        super().__init__()
        self.notebook_area = notebook_area
        self.pages = QtWidgets.QStackedWidget()
        self.pages_list = []
        if pages:
            for page in pages:
                self.add_page_local(DrawingCanvas(**(pages[page]),
                                            notebook_area=notebook_area))
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
        notebook_dict = {
            "pages": page_dict,
            "last_change": self.last_change
        }
        return notebook_dict

    def current_canvas(self):
        """return current canvas"""
        return self.pages.currentWidget()

    def add_page_local(self, page, set_as_current: bool = True):
        """add another canvas locally without updating the server
        
        :param page: The canvas page to add, or None to create a new one
        :param set_as_current: Whether to set the new page as the current page, default: True
        """
        if page:
            canvas = page
        else:
            canvas = DrawingCanvas(*CANVAS_SIZE, None,
                                   None, self.notebook_area,
                                   None,
                                   self.pages.currentIndex() + NEXT_PAGE)
        if self.pages_list:
            prev_canvas = self.pages_list[LAST_PAGE_INDEX]
            canvas.scale_factor = prev_canvas.scale_factor
            canvas._update_size()
        self.pages_list.append(canvas)
        self.pages.addWidget(canvas)
        if set_as_current:
            self.pages.setCurrentWidget(canvas)
        if self.notebook_area and self.notebook_area.notebook_widget:
            self.notebook_area.add_page_local(canvas.id, canvas)
            if set_as_current:
                self.notebook_area.current_page = self.pages.currentIndex()

    def add_page(self, page):
        """add another canvas and update the server"""
        if page:
            canvas = page
        else:
            canvas = DrawingCanvas(*CANVAS_SIZE, None,
                                   None, self.notebook_area,
                                   None,
                                   self.pages.currentIndex() + NEXT_PAGE)
        if self.pages_list:
            prev_canvas = self.pages_list[LAST_PAGE_INDEX]
            canvas.scale_factor = prev_canvas.scale_factor
            canvas._update_size()
        self.pages_list.append(canvas)
        self.pages.addWidget(canvas)
        self.pages.setCurrentWidget(canvas)
        if self.notebook_area and self.notebook_area.notebook_widget:
            self.notebook_area.add_page(canvas.id, canvas)
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

    def update_notebook(self, ts, type, page, data):
        """update the notebook from the DB
        
        :param ts: timestamp of the update
        :param type: type of update (ADD_PAGE, CHANGE_BACKGROUND, etc.)
        :param page: page ID for the update
        :param data: data for the update (page data for ADD_PAGE, background type for CHANGE_BACKGROUND, etc.)
        """
        if type == "ADD_PAGE":
            # Check if page with this ID already exists to avoid duplicates
            page_id = int(page) if page else None
            if page_id is not None:
                for existing_page in self.pages_list:
                    if existing_page.id == page_id:
                        # Page already exists, skip adding
                        self.last_change = float(ts)
                        return
            
            # Create canvas from the page data received from server
            if data and isinstance(data, dict):
                new_canvas = DrawingCanvas(**data, notebook_area=self.notebook_area)
            else:
                new_canvas = None
            # Don't switch to the new page - preserve current page
            self.add_page_local(new_canvas, set_as_current=False)
        else:
            for p in self.pages_list:
                if p.id == int(page):
                    cls = getattr(canvas, "DrawingCanvas")
                    getattr(cls, type)(p, data)
        self.last_change = float(ts)

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
