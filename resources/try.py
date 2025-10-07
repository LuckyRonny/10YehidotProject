from PyQt6 import QtWidgets, QtGui, QtCore
import sys

# --- Placeholder constants (replace with your style.py values) ---
WINDOW_SIZE = (1000, 700)
CANVAS_SIZE = (800, 600)
MARGIN = (10, 10, 10, 10)
BUTTON_SIZE = (80, 30)
BUTTON_WIDTH = 50
SUB_TOOLBAR = ""
MAIN_WINDOW = ""
PEN_RANGE = (1, 50)
PEN_START_VALUE = 5
PEN_STEP = 1
MARKER_RANGE = (5, 50)
MARKER_START_VALUE = 10
MARKER_STEP = 1
ERASER_RANGE = (5, 50)
ERASER_START_VALUE = 10
ERASER_STEP = 1
COLORS_NAMES = ["black", "red", "green", "blue"]
MARKER_COLORS_NAMES = ["yellow", "orange", "pink", "lightblue"]
TEXT_RANGE = (10, 100)
TEXT_START_VALUE = 20
TEXT_STEP = 5


# --- Toolbars Enum ---
from enum import Enum


class ToolbarsEnum(Enum):
    PAGE = 0
    PEN = 1
    MARKER = 2
    ERASER = 3
    SELECT = 4
# --- Drawing Canvas ---
class Stroke:
    def __init__(self, points, pen_color, pen_size):
        self.points = points
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.selected = False

    def contains_point(self, pt, tolerance=5):
        for i in range(1, len(self.points)):
            p1, p2 = self.points[i-1], self.points[i]
            if self._point_line_distance(pt, p1, p2) <= tolerance:
                return True
        return False

    @staticmethod
    def _point_line_distance(p, a, b):
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        px, py = p.x(), p.y()
        dx, dy = bx - ax, by - ay
        if dx == dy == 0:
            return ((px - ax)**2 + (py - ay)**2) ** 0.5
        t = max(0, min(1, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
        closest_x = ax + t*dx
        closest_y = ay + t*dy
        return ((px - closest_x)**2 + (py - closest_y)**2) ** 0.5

class DrawingCanvas(QtWidgets.QWidget):
    def __init__(self, width=800, height=600):
        super().__init__()
        self.setFixedSize(width, height)
        self.background_layer = QtGui.QPixmap(self.size())
        self.background_layer.fill(QtCore.Qt.GlobalColor.white)

        self.strokes = []
        self.current_stroke_points = []

        self.drawing = False
        self.selected_stroke = None
        self.pen_color = QtGui.QColor("black")
        self.pen_size = 5

        self.scale_factor = 1.0

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        painter.save()
        painter.scale(self.scale_factor, self.scale_factor)
        painter.drawPixmap(0, 0, self.background_layer)
        painter.restore()

        painter.save()
        painter.scale(self.scale_factor, self.scale_factor)

        # Draw all strokes
        for stroke in self.strokes:
            pen = QtGui.QPen(stroke.pen_color, stroke.pen_size)
            painter.setPen(pen)
            pts = stroke.points
            if len(pts) > 1:
                for i in range(1, len(pts)):
                    painter.drawLine(pts[i-1], pts[i])
            if stroke.selected:
                highlight = QtGui.QPen(QtGui.QColor("red"), stroke.pen_size+2)
                highlight.setStyle(QtCore.Qt.PenStyle.DashLine)
                painter.setPen(highlight)
                for i in range(1, len(pts)):
                    painter.drawLine(pts[i-1], pts[i])

        # Draw current stroke
        if self.drawing and len(self.current_stroke_points) > 1:
            pen = QtGui.QPen(self.pen_color, self.pen_size)
            painter.setPen(pen)
            pts = self.current_stroke_points
            for i in range(1, len(pts)):
                painter.drawLine(pts[i-1], pts[i])
        painter.restore()

    def mousePressEvent(self, event):
        pos = (event.position() / self.scale_factor).toPoint()
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            clicked_stroke = None
            for stroke in reversed(self.strokes):
                if stroke.contains_point(pos):
                    clicked_stroke = stroke
                    break
            if clicked_stroke:
                self.selected_stroke = clicked_stroke
                clicked_stroke.selected = True
                self.prev_mouse_pos = pos
            else:
                self.drawing = True
                self.current_stroke_points = [pos]
                self.selected_stroke = None
                for s in self.strokes:
                    s.selected = False
            self.update()

    def mouseMoveEvent(self, event):
        pos = (event.position() / self.scale_factor).toPoint()
        if self.drawing:
            self.current_stroke_points.append(pos)
            self.update()
        elif self.selected_stroke:
            dx = pos.x() - self.prev_mouse_pos.x()
            dy = pos.y() - self.prev_mouse_pos.y()
            for i, p in enumerate(self.selected_stroke.points):
                self.selected_stroke.points[i] = QtCore.QPoint(p.x()+dx, p.y()+dy)
            self.prev_mouse_pos = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if self.drawing:
            if len(self.current_stroke_points) > 1:
                self.strokes.append(Stroke(self.current_stroke_points.copy(),
                                           self.pen_color, self.pen_size))
            self.current_stroke_points = []
            self.drawing = False
            self.update()
        self.selected_stroke = None

    def zoom_in(self):
        self.scale_factor *= 1.2
        self.update()
    def zoom_out(self):
        self.scale_factor /= 1.2
        self.update()
    def change_pen_size(self, val):
        self.pen_size = val
    def change_pen_color(self, index):
        try:
            self.pen_color = QtGui.QColor(COLORS_NAMES[index])
        except:
            self.pen_color = QtGui.QColor("black")
    def clear_canvas(self):
        self.strokes = []
        self.update()
    def save_canvas(self):
        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)
        pixmap.save("drawing.png")
    def back(self):
        if self.strokes:
            self.strokes.pop()
            self.update()

# --- Scroll Area ---
class CanvasContainer(QtWidgets.QWidget):
    def __init__(self, child_widget):
        super().__init__()
        self.child_widget = child_widget
        layout = QtWidgets.QVBoxLayout()
        layout.addStretch(1)
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(child_widget)
        h_layout.addStretch(1)
        layout.addLayout(h_layout)
        layout.addStretch(1)
        self.setLayout(layout)

class CenteredScrollArea(QtWidgets.QScrollArea):
    def __init__(self, canvas_widget):
        super().__init__()
        self.canvas_widget = canvas_widget
        self.setWidgetResizable(True)
        container = CanvasContainer(canvas_widget)
        self.setWidget(container)
    def wheelEvent(self, event):
        if (QtWidgets.QApplication.keyboardModifiers() ==
            QtCore.Qt.KeyboardModifier.ControlModifier):
            if event.angleDelta().y() > 0:
                self.canvas_widget.zoom_in()
            else:
                self.canvas_widget.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

# --- Main Window ---
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(*WINDOW_SIZE)
        self.canvas_widget = DrawingCanvas(*CANVAS_SIZE)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QtWidgets.QVBoxLayout()
        central_layout.setContentsMargins(*MARGIN)
        central_widget.setLayout(central_layout)

        self.main_toolbar = QtWidgets.QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        scroll_area = CenteredScrollArea(self.canvas_widget)
        central_layout.addWidget(scroll_area)

        # Add clear/save/back buttons
        for name, func in [("Clear", self.canvas_widget.clear_canvas),
                           ("Save", self.canvas_widget.save_canvas),
                           ("Back", self.canvas_widget.back)]:
            btn = QtWidgets.QPushButton(name)
            btn.clicked.connect(func)
            self.main_toolbar.addWidget(btn)

# --- Run ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
