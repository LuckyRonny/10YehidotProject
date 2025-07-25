import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from style import *

WINDOW_SIZE = (650, 650)
CANVAS_SIZE = (450, 550)
BUTTON_SIZE = (60, 30)
COLORS = ["#000000", "#A1A1A1", "#FFFFFF", "#C0C0C0", "#F7CF49", "#DC143C",
          "#FFB662", "#F6ED6B", "#98FB98", "#9AD7FF", "#4983E6",
          "#A873F7", "#F0AEEA"]
COLORS_NAMES = ["black", "gray", "white", "silver", "gold", "red", "orange",
                "yellow", "green", "light blue", "blue",
                "purple", "pink"]
MARKER_COLORS = ["#DC143C", "#FFB662", "#F6ED6B", "#98FB98", "#9AD7FF",
                 "#4983E6", "#A873F7", "#F0AEEA"]
MARKER_COLORS_NAMES = ["red", "orange", "yellow", "green", "light blue",
                       "blue", "purple", "pink"]


class DrawingCanvas(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        self.canvas = QtGui.QPixmap(self.size())
        self.canvas.fill(Qt.GlobalColor.white)

        self.drawing = False
        self.last_point = QtCore.QPoint()

        self.pen_color = QtGui.QColor("black")
        self.pen_size = 1
        self.tool = "pen"

        self.scale_factor = 1.0
        self.base_width = width
        self.base_height = height
        self.history = []
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: #ADD8E6;")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.drawPixmap(0, 0, self.canvas)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.history.append(self.canvas.copy())
            self.last_point = (event.position() / self.scale_factor).toPoint()

    def mouseMoveEvent(self, event):
        if self.drawing:
            current_point = (event.position() / self.scale_factor).toPoint()
            painter = QtGui.QPainter(self.canvas)
            pen = QtGui.QPen(self.pen_color,
                             self.pen_size,
                             Qt.PenStyle.SolidLine,
                             Qt.PenCapStyle.RoundCap)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawLine(self.last_point, current_point)
            painter.end()
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def clear_canvas(self):
        self.canvas.fill(Qt.GlobalColor.white)
        self.update()

    def save_canvas(self):
        self.canvas.save("canvas.png", "PNG")
        QMessageBox.information(self, "Saved", "saved")

    def change_pen_size(self, size):
        self.pen_size = size

    def set_tool(self, tool_type):
        self.tool = tool_type

    def change_pen_color(self, i):
        if self.tool == "marker":
            color = QtGui.QColor(MARKER_COLORS[i])
            color.setAlpha(30)
        else:
            color = QtGui.QColor(COLORS[i])
            color.setAlpha(255)
        self.pen_color = color

    def back(self):
        if self.history:
            self.canvas = self.history.pop()
            self.update()

    def zoom_in(self):
        self.scale_factor *= 1.2
        self._update_size()

    def zoom_out(self):
        self.scale_factor /= 1.2
        self._update_size()

    def _update_size(self):
        new_width = int(self.base_width * self.scale_factor)
        new_height = int(self.base_height * self.scale_factor)
        self.setFixedSize(new_width, new_height)
        self.update()


class CenteredScrollArea(QScrollArea):
    def __init__(self, canvas_widget):
        super().__init__()
        self.canvas_widget = canvas_widget
        self.setWidgetResizable(True)

        container = QWidget()
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(canvas_widget)
        h_layout.addStretch(1)
        v_layout.addLayout(h_layout)
        container.setLayout(v_layout)

        self.setWidget(container)

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.canvas_widget.zoom_in()
            else:
                self.canvas_widget.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(MAIN_WINDOW)
        self.setMinimumSize(*WINDOW_SIZE)

        self.canvas_widget = DrawingCanvas(*CANVAS_SIZE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(central_layout)

        self.pen_size_button = QSpinBox()
        self.pen_size_button.setRange(1, 10)
        self.pen_size_button.setValue(1)
        self.pen_size_button.setMinimumWidth(50)
        self.pen_size_button.valueChanged.connect(
            self.canvas_widget.change_pen_size)

        self.pen_color_button = QComboBox()
        self.pen_color_button.addItems(COLORS_NAMES)
        self.pen_color_button.currentIndexChanged.connect(
            self.canvas_widget.change_pen_color)

        self.marker_size_button = QSpinBox()
        self.marker_size_button.setRange(10, 100)
        self.marker_size_button.setValue(30)
        self.marker_size_button.setMinimumWidth(50)
        self.marker_size_button.valueChanged.connect(
            self.canvas_widget.change_pen_size)

        self.marker_color_button = QComboBox()
        self.marker_color_button.addItems(MARKER_COLORS_NAMES)
        self.marker_color_button.currentIndexChanged.connect(
            self.canvas_widget.change_pen_color)

        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.sub_toolbars = []

        pen_toolbar = QToolBar("pen")
        pen_toolbar.setMovable(False)
        pen_toolbar.setFloatable(False)
        pen_toolbar.setVisible(False)
        pen_toolbar.setStyleSheet(SUB_TOOLBAR)
        pen_toolbar.addWidget(self.pen_size_button)
        pen_toolbar.addWidget(self.pen_color_button)
        self.sub_toolbars.append(pen_toolbar)
        central_layout.addWidget(pen_toolbar)

        marker_toolbar = QToolBar("marker")
        marker_toolbar.setMovable(False)
        marker_toolbar.setFloatable(False)
        marker_toolbar.setVisible(False)
        marker_toolbar.setStyleSheet(SUB_TOOLBAR)
        marker_toolbar.addWidget(self.marker_size_button)
        marker_toolbar.addWidget(self.marker_color_button)
        self.sub_toolbars.append(marker_toolbar)
        central_layout.addWidget(marker_toolbar)

        self.pen_button = QPushButton("pen", self)
        self.pen_button.setCheckable(True)
        self.pen_button.setFixedSize(*BUTTON_SIZE)
        self.pen_button.clicked.connect(
            lambda checked, x=0: self.show_sub_toolbar(x))
        self.main_toolbar.addWidget(self.pen_button)

        self.marker_button = QPushButton("marker", self)
        self.marker_button.setCheckable(True)
        self.marker_button.setFixedSize(*BUTTON_SIZE)
        self.marker_button.clicked.connect(
            lambda checked, x=1: self.show_sub_toolbar(x))
        self.main_toolbar.addWidget(self.marker_button)

        clear_button = QPushButton("clear", self)
        clear_button.clicked.connect(self.canvas_widget.clear_canvas)
        clear_button.setFixedSize(*BUTTON_SIZE)
        clear_button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(clear_button)

        save_button = QPushButton("save", self)
        save_button.clicked.connect(self.canvas_widget.save_canvas)
        save_button.setFixedSize(*BUTTON_SIZE)
        save_button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(save_button)

        back_button = QPushButton("back", self)
        back_button.clicked.connect(self.canvas_widget.back)
        back_button.setFixedSize(*BUTTON_SIZE)
        back_button.setStyleSheet(BUTTON)
        self.main_toolbar.addWidget(back_button)

        scroll_area = CenteredScrollArea(self.canvas_widget)
        central_layout.addWidget(scroll_area)

    def show_sub_toolbar(self, index):
        for i, toolbar in enumerate(self.sub_toolbars):
            is_selected = (i == index)
            toolbar.setVisible(is_selected)
            self.pen_button.setChecked(i == 0 and is_selected)
            self.marker_button.setChecked(i == 1 and is_selected)
            if is_selected:
                if i == 0:
                    self.canvas_widget.set_tool("pen")
                    self.canvas_widget.change_pen_color(
                        self.pen_color_button.currentIndex())
                    self.canvas_widget.change_pen_size(
                        self.pen_size_button.value())
                elif i == 1:
                    self.canvas_widget.set_tool("marker")
                    self.canvas_widget.change_pen_color(
                        self.marker_color_button.currentIndex())
                    self.canvas_widget.change_pen_size(
                        self.marker_size_button.value())


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
