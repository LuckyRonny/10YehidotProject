"""

"""

import sys
import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import os

COLORS = ["#000000", "#A1A1A1", "#FFFFFF", "#C0C0C0", "#F7CF49", "#DC143C",
          "#FFB662", "#F6ED6B", "#98FB98", "#9AD7FF", "#4983E6",
          "#A873F7", "#F0AEEA",]
COLORS_NAMES = ["black", "gray", "white", "silver", "gold", "red", "orange",
                "yellow", "green", "light blue", "blue",
                "purple", "pink"]

MARKER_COLORS = ["#000000", "#A1A1A1", "#FFFFFF", "#DC143C", "#FFB662",
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