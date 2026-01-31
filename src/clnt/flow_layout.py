"""
Ronny Getz
flow layout
"""

from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import QRect, QPoint, QSize, Qt

DEFAULT_MARGIN = (0, 0, 0, 0)
DEFAULT_SPACING = 5
FIRST_ITEM = 0

RECT_TEST_HEIGHT = 0
INITIAL_OFFSET_X = 0
INITIAL_OFFSET_Y = 0
NO_EXPANSION = 0
SUBTRACT_SPACING = 1
MINIMUM_SIZE_ADD_X = 1
MINIMUM_SIZE_ADD_Y = 1
RIGHT_EDGE_CORRECTION = 0
START_LINE_HEIGHT = 0


class FlowLayout(QLayout):
    """
    A custom layout that arranges widgets in a flowing style that when there is
    no more horizontal space, they wrap onto the next line.
    """

    def __init__(self, parent=None):
        """
        Create a new FlowLayout.
        """
        super().__init__(parent)
        self.itemList = []
        self.setContentsMargins(*DEFAULT_MARGIN)
        self.setSpacing(DEFAULT_SPACING)

    def addItem(self, item):
        """Add an item (wrapped widget) to the layout."""
        self.itemList.append(item)

    def count(self):
        """Return the number of items in the layout."""
        return len(self.itemList)

    def itemAt(self, index):
        """Return the item at a given index, or None if not found."""
        if FIRST_ITEM <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        """Remove and return the item at the given index,
        or None if not found."""
        if FIRST_ITEM <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        """Indicate that the layout does not expand automatically."""
        return Qt.Orientation(NO_EXPANSION)

    def hasHeightForWidth(self):
        """Specify that height depends on width."""
        return True

    def heightForWidth(self, width):
        """
        Compute needed height for a given width.
        """
        return self.do_layout(
            QRect(INITIAL_OFFSET_X, INITIAL_OFFSET_Y, width, RECT_TEST_HEIGHT),
            test_only=True
        )

    def setGeometry(self, rect):
        """Apply geometry and place items."""
        super().setGeometry(rect)
        self.do_layout(rect, test_only=False)

    def sizeHint(self):
        """General recommended size."""
        return self.minimumSize()

    def minimumSize(self):
        """Compute minimum size required to display all items."""
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(
            (margins.left() + margins.right()) * MINIMUM_SIZE_ADD_X,
            (margins.top() + margins.bottom()) * MINIMUM_SIZE_ADD_Y
        )
        return size

    def do_layout(self, rect, test_only):
        """Compute or apply the item layout depending on test_only."""
        x, y = rect.x(), rect.y()
        spacing_x = spacing_y = self.spacing()
        line_height = START_LINE_HEIGHT
        for item in self.itemList:
            item_width, item_height = (item.sizeHint().width(),
                                       item.sizeHint().height())
            x, y, line_height = self.process_item(
                item, rect, x, y, line_height, spacing_x, spacing_y, test_only
            )
        return y + line_height - rect.y()

    def process_item(self, item, rect, x, y, line_height, spacing_x, spacing_y,
                     test_only):
        """Handle placement and wrapping logic for a single item."""
        next_x = x + item.sizeHint().width() + spacing_x
        if (
                next_x - spacing_x - SUBTRACT_SPACING > rect.right() -
                RIGHT_EDGE_CORRECTION and line_height > START_LINE_HEIGHT):
            x = rect.x()
            y += line_height + spacing_y
            next_x = x + item.sizeHint().width() + spacing_x
            line_height = START_LINE_HEIGHT
        if not test_only:
            item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
        line_height = max(line_height, item.sizeHint().height())
        return next_x, y, line_height

    def clear(self, delete_widgets=True):
        """
        Remove all items from the layout.
        If delete_widgets is True, also delete the widgets themselves.
        """
        while self.itemList:
            item = self.takeAt(0)
            if delete_widgets:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def reset_items(self, new_widgets=None):
        """
        Clear all current items and optionally add new widgets.
        `new_widgets` should be a list of QWidget instances.
        """
        self.clear(delete_widgets=True)
        if new_widgets:
            for widget in new_widgets:
                self.addWidget(widget)
