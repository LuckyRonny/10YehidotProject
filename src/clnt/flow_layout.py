"""
Ronny Getz
flow layout
"""

from PyQt6.QtWidgets import QLayout, QSizePolicy
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
        """Remove and return the item at the given index, or None if not found."""
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
        return self.doLayout(
            QRect(INITIAL_OFFSET_X, INITIAL_OFFSET_Y, width, RECT_TEST_HEIGHT),
            testOnly=True
        )

    def setGeometry(self, rect):
        """Apply geometry and place items."""
        super().setGeometry(rect)
        self.doLayout(rect, testOnly=False)

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

    def doLayout(self, rect, testOnly):
        """
        Perform layout calculation and optionally place widgets.
        """
        x = rect.x()
        y = rect.y()
        lineHeight = START_LINE_HEIGHT

        spacingX = self.spacing()
        spacingY = self.spacing()

        for item in self.itemList:
            itemWidth = item.sizeHint().width()
            itemHeight = item.sizeHint().height()

            nextX = x + itemWidth + spacingX

            if nextX - spacingX - SUBTRACT_SPACING > rect.right() - RIGHT_EDGE_CORRECTION and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spacingY
                nextX = x + itemWidth + spacingX
                lineHeight = START_LINE_HEIGHT

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, itemHeight)

        return y + lineHeight - rect.y()
