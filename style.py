"""
Ronny Getz
imports, magic numbers and style
"""

import sys
import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import os

WINDOW_SIZE = (650, 650)
CANVAS_SIZE = (550, 700)
ROW_LIMITS = (0, CANVAS_SIZE[0])
COLUMN_LIMITS = (0, CANVAS_SIZE[1])
TOOLBARS_POSITION = (0, 0, 0, 0)
PEN_RANGE = (1, 10)
PEN_START_VALUE = 3
PEN_STEP = 1
ERASER_RANGE = (5, 50)
ERASER_START_VALUE = 10
ERASER_STEP = 5
MARKER_RANGE = (10, 100)
MARKER_START_VALUE = 20
MARKER_STEP = 10
BUTTON_WIDTH = 50
MARGIN = (0, 0, 0, 0)
SPACER = (0, 0)
BUTTON_SIZE = (60, 30)
PAGE_INDEX = 0
PEN_INDEX = 1
MARKER_INDEX = 2
ERASER_INDEX = 3
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
BACKROUND_PEN_SIZE = 0.5
CLEAR_COLOR = (0, 0, 0, 0)
TIME_OF_POINT_INDEX = 1
CLOSE_POINTS_TIME = 1E9
CLOSE_POINTS_DISTANCE = 5
LAST_POINT = -1
POINT_INDEX = 0
SCALE_CHANGE = 1.2
SCALE_MAX = 5.0
SCALE_MIN = 0.5


COLORS = ["#393939", "#A1A1A1", "#FFFFFF", "#C0C0C0", "#F7CF49", "#DC143C",
          "#FFB662", "#F6ED6B", "#98FB98", "#9AD7FF", "#4983E6",
          "#A873F7", "#F0AEEA",]
COLORS_NAMES = ["black", "gray", "white", "silver", "gold", "red", "orange",
                "yellow", "green", "light blue", "blue",
                "purple", "pink"]

MARKER_COLORS = ["#393939", "#A1A1A1", "#FFFFFF", "#DC143C", "#FFB662",
                 "#F6ED6B", "#98FB98", "#9AD7FF",
                 "#4983E6", "#A873F7", "#F0AEEA"]
MARKER_COLORS_NAMES = ["black", "gray", "white", "red", "orange",
                       "yellow", "green", "light blue",
                       "blue", "purple", "pink"]

MAIN_WINDOW = """
            QMainWindow {
                background: #D3E9FF;
            }
            QToolBar {
                background: #6894EB;
                padding: 0px;
                border: 0px;
            }
            QPushButton {
                background: #6894EB;
                color: #FFFFFF;
                font: bold 14px;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }  
            QPushButton:hover{
                background: #D3E9FF;
                color: #FFFFFF;
                font: bold 14px;
            }  
            QSpinBox::down-button:hover { 
                background-color: #D0E0FF;
            }
            QSpinBox::up-button:hover { 
                background-color: #D0E0FF;
            }
            QSpinBox{
                background: #D0E0FF;
                min-height: 25px;
                min-width: 35px;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox{
                background: #D0E0FF;
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
                background: #D0E0FF;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox QAbstractItemView {
                background: #D0E0FF;
                font: bold 14px;
                color: #FFFFFF;
                border-style: outset;
                border-width: 2px;
                border-radius: 1px;
                border-color: #D3E9FF;
            }
            QComboBox::item {
                background: #D0E0FF;
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
                background: #769FF3;
            }
            QScrollBar:horizontal {
                background: #D3E9FF;
            }
            QScrollBar::handle:horizontal {
                background: #769FF3;
            }
            """
SUB_TOOLBAR = """
                background: #7BA5F9;
            """
BUTTON = """
                QPushButton:hover {
                    background-color: #D3E9FF;
                }
            """