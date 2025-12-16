"""
Ronny Getz
magic numbers and style
"""

from enum import Enum


class ToolbarsEnum(Enum):
    PAGE = 0
    PEN = 1
    MARKER = 2
    ERASER = 3
    SELECT = 4


# window
WINDOW_SIZE = (650, 650)
MARGIN = (0, 0, 0, 0)
SPACER = (0, 0)

# canvas & background
CANVAS_SIZE = (550, 700)
START_PIXMAP = 0
STRETCH = 1
START_ANGLE = 0
ROW_LIMITS = (0, CANVAS_SIZE[0])
COLUMN_LIMITS = (0, CANVAS_SIZE[1])
LINE_MARGIN = 50
LEFT_LINE = (LINE_MARGIN, 0, LINE_MARGIN, CANVAS_SIZE[1])
RIGHT_LINE = (CANVAS_SIZE[0]-LINE_MARGIN, 0, CANVAS_SIZE[0]-LINE_MARGIN,
              CANVAS_SIZE[1])
START_LINE = 50
END_LINE = CANVAS_SIZE[1]
NUMBER_LINES = 30
START_GRID = 0
END_GRID = (CANVAS_SIZE[1], CANVAS_SIZE[0])
NUMBER_LINES_GRID = 45
ROW_INDEX = 0
COLUMN_INDEX = 1
BACKGROUND_PEN_SIZE = 0.5

# toolbar
TOOLBARS_POSITION = (0, 0, 0, 0)
# pen
PEN_RANGE = (1, 25)
PEN_START_VALUE = 5
PEN_STEP = 1
TRANSPARENCY_PEN = 255
PEN_SIZE_FACTOR = 2
ADD_SELECTED_PEN_SIZE = 1
# eraser
ERASER_RANGE = (5, 50)
ERASER_START_VALUE = 10
ERASER_STEP = 5
ERASER_TOLERANCE = 1.5
# marker
MARKER_RANGE = (10, 100)
MARKER_START_VALUE = 20
MARKER_STEP = 10
TRANSPARENCY_MARKER = 80

# button
BUTTON_WIDTH = 60
BUTTON_SIZE = (60, 30)

# colors
CLEAR_COLOR = (0, 0, 0, 0)
LIGHTER_COLOR = 130

# straight line
CLOSE_POINTS_TIME = 1E9
CLOSE_POINTS_DISTANCE = 10
MARKER_LINE_TIMES = 4
LAST_POINT = -1

# zoom in
START_SCALE_FACTOR = 1.0
SCALE_CHANGE = 1.2
SCALE_MAX = 5.0
SCALE_MIN = 0.5
SCROLL_AREA = 0
SCROLL_STRETCH = 1

# distance
SQUARED = 2
SQUARE_ROOT = 0.5

# points
EMPTY_POINT_LIST = 0
SAME_POINT = 0
LINE_POINT_START = 0
LINE_POINT_END = 1
SECOND_POINT = 1
POINT_BEFORE = 1
ONLY_ONE_POINT = 1
LESS_THEN_TWO_POINTS = 2
POINT_AFTER = 1
STROKE_POINT_START = 0
STROKE_POINT_END = -1

# file
FILE_EXTENSION = -1

# select
SELECTED_TOLERANCE = 2

# pages
LAST_PAGE_INDEX = -1
PREV_PAGE = 1
NEXT_PAGE = 1
NO_PAGES = 0
FIRST_PAGE = 0

# scroll
NO_ENGLE = 0

# log in & sign up
LOGIN_STRETCH = 15
LINE_EDIT_MAX_LENGTH = 20
BUTTON_HEIGHT = 25

# main window
ADD_NOTEBOOK_SIZE = 40
ADD_BUTTON_SIZE = (40, 40)
NOTEBOOK_BUTTON_SIZE = (150, 225)
BOX_LINE_SIZE = 2
BOX_SIZE = (250, 150)
BOX_MARGIN_RIGHT = 20
BOX_MARGIN_LEFT = 10
BOX_MIN_MARGIN = 0


COLORS = ["#393939", "#A1A1A1", "#FFFFFF", "#C0C0C0", "#F7CF49", "#DC143C",
          "#FFB662", "#F6ED6B", "#98FB98", "#9AD7FF", "#4983E6",
          "#A873F7", "#F0AEEA"]
COLORS_NAMES = ["black", "gray", "white", "silver", "gold", "red", "orange",
                "yellow", "green", "light blue", "blue",
                "purple", "pink"]

MARKER_COLORS = ["#393939", "#A1A1A1", "#FFFFFF", "#F36565", "#F3B165",
                 "#FAFA80", "#B5FA80", "#9FF5EF",
                 "#74A5EE", "#A683F6", "#EFACF6"]
MARKER_COLORS_NAMES = ["black", "gray", "white", "red", "orange",
                       "yellow", "green", "light blue",
                       "blue", "purple", "pink"]

MAIN_WINDOW = """
            QMainWindow {
                background: #D3E9FF;
            }
            QStackedWidget {
                background-color: #D3E9FF;
            }
            QWidget {
                background-color: #D3E9FF;
            }
            QToolBar {
                background: #1B0BA6;
                padding: 0px;
                border: 0px;
            }
            QPushButton {
                background: #1B0BA6;
                color: #FFFFFF;
                font: 14px;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
                font-family: broadway;
            }
            QPushButton:hover{
                background: #D3E9FF;
                color: #FFFFFF;
                font: 14px;
                font-family: broadway;
            }
            QSpinBox::down-button:hover {
                background-color: #1B0BA6;
            }
            QSpinBox::up-button:hover {
                background-color: #1B0BA6;
            }
            QSpinBox{
                background: #1B0BA6;
                min-height: 25px;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QSpinBox::edit-field {
                padding-left: 22px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #D3E9FF;
            }
            QComboBox{
                background: #1B0BA6;
                min-height: 25px;
                min-width: 45px;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox::button{
                background: #1B0BA6;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox QAbstractItemView {
                background: #1B0BA6;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox::item {
                background: #1B0BA6;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox::item:selected {
                background-color: #D3E9FF;
            }
            QComboBox::item:hover {
                background-color: #D3E9FF;
            }
            QMessageBox {
                background-color: #7BA5F9;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
                font: bold 16px
            }
            QScrollArea {
                background-color: #D3E9FF;
            }
            QScrollBar:vertical {
                background: #D3E9FF;
            }
            QScrollBar::handle:vertical {
                background: #1B0BA6;
            }
            QScrollBar:horizontal {
                background: #D3E9FF;
            }
            QScrollBar::handle:horizontal {
                background: #1B0BA6;
            }
            QLabel {
                color: #1B0BA6;
                font: bold 16px;
                border-style: outset;
                font-family: broadway;
            }
            QLineEdit {
                border: 2px solid #1B0BA6;
                border-radius: 2px;
                padding: 3px;
                background-color: #F0F0F0;
                color: #1B0BA6;
                font-size: 14px;
                font-family: broadway;
            }
            """
ADD_NOTEBOOK_BUTTON = """
                        QPushButton {
                            background-color: #1B0BA6;
                            border: 0px
                        }
                        QPushButton:hover {
                            background-color: #5B4CE6;
                        }
                    """
LOGOUT_BUTTON = """
                QPushButton {
                    background-color: #1B0BA6;
                    font: bold 14px;
                    padding: 3px;
                    font-family: broadway;
                    border: 0px
                }
                QPushButton:hover {
                    background-color: #5B4CE6;
                }
                """
NAME_LABEL = """
                background-color: #1B0BA6;
                color: #FFFFFF;
                font: bold 14px;
                border-style: outset;
                font-family: broadway;
            """
SUB_TOOLBAR = """
                background: #2E1EBC;
            """
BUTTON = """
                QPushButton:hover {
                    background-color: #D3E9FF;
                }
            """
LOGIN_BUTTON = """
                background: #1B0BA6;
                color: #FFFFFF;
                font: bold 13px;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
                font-family: broadway;
        """
ADD_NOTEBOOK_FRAME = """
                    QFrame {
                        background-color: #D3E9FF;
                        border-style: outset;
                        border-width: 3px;
                        border-radius: 1px;
                        border-color: #1B0BA6;
                    }
                    QPushButton {
                        background-color: #1B0BA6;
                        font: bold 14px;
                        padding: 3px;
                        font-family: broadway;
                        border: 0px
                    }
                    QPushButton:hover {
                        background-color: #5B4CE6;
                    }
                    QLabel {
                        color: #1B0BA6;
                        font: bold 16px;
                        border-style: outset;
                        font-family: broadway;
                        border: false
                    }
                    QLineEdit {
                        border: 2px solid #1B0BA6;
                        border-radius: 2px;
                        padding: 3px;
                        background-color: #F0F0F0;
                        color: #1B0BA6;
                        font-size: 14px;
                        font-family: broadway;
                    }
                    """
