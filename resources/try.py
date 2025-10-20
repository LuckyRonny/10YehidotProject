import sys
from PyQt6 import QtWidgets, QtGui, QtCore

# --- הגדרות ראשוניות ---
START_WIDTH = 800
START_HEIGHT = 600

# צבעים
COLORS = ["black", "red", "green", "blue", "yellow"]
MARKER_COLORS = ["red", "green", "blue", "yellow"]

# --- Stroke class פשוט ---
class Stroke:
    def __init__(self, points, pen_color, pen_size):
        self.points = points
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.selected = False

# --- Canvas class ---
class DrawingCanvas(QtWidgets.QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        self.strokes = []
        self.current_stroke_points = []
        self.drawing = False
        self.tool = "pen"
        self.pen_color = QtGui.QColor("black")
        self.pen_size = 5
        self.marker_alpha = 120

        # רקע
        self.background_layer = QtGui.QPixmap(self.size())
        self.background_layer.fill(QtCore.Qt.GlobalColor.white)

        self.selected_stroke = None
        self.last_point = QtCore.QPoint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.background_layer)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # לצייר את כל הקווים
        for stroke in self.strokes:
            pen = QtGui.QPen(stroke.pen_color, stroke.pen_size)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            pts = stroke.points
            if len(pts) > 1:
                for i in range(1, len(pts)):
                    painter.drawLine(pts[i - 1], pts[i])

        # לצייר את הקו הנוכחי בזמן גרירה
        if self.drawing and len(self.current_stroke_points) > 1:
            pen = QtGui.QPen(self.pen_color, self.pen_size)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            pts = self.current_stroke_points
            for i in range(1, len(pts)):
                painter.drawLine(pts[i - 1], pts[i])

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self.tool in ["pen", "marker"]:
                self.drawing = True
                self.current_stroke_points = [pos]
            elif self.tool == "eraser":
                self.erase_points(pos)
            elif self.tool == "select":
                self.selected_stroke = None
                for stroke in reversed(self.strokes):
                    for p in stroke.points:
                        if (p - pos).manhattanLength() < 10:
                            stroke.selected = True
                            self.selected_stroke = stroke
                            self.last_point = pos
                            break
                    else:
                        stroke.selected = False
                self.update()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self.drawing and self.tool in ["pen", "marker"]:
            self.current_stroke_points.append(pos)
            self.update()
        elif self.tool == "eraser" and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.erase_points(pos)
        elif self.tool == "select" and self.selected_stroke and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            dx = pos.x() - self.last_point.x()
            dy = pos.y() - self.last_point.y()
            self.selected_stroke.points = [QtCore.QPoint(p.x() + dx, p.y() + dy) for p in self.selected_stroke.points]
            self.last_point = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if self.tool in ["pen", "marker"] and self.drawing:
            self.drawing = False
            stroke = Stroke(points=self.current_stroke_points[:], pen_color=self.pen_color, pen_size=self.pen_size)
            self.strokes.append(stroke)
            self.current_stroke_points = []
            self.update()

    def erase_points(self, pos):
        new_strokes = []
        for stroke in self.strokes:
            new_points = [p for p in stroke.points if (p - pos).manhattanLength() > self.pen_size * 1.5]
            if len(new_points) > 1:
                new_strokes.append(Stroke(new_points, stroke.pen_color, stroke.pen_size))
        self.strokes = new_strokes
        self.update()

    def set_tool(self, tool_type):
        self.tool = tool_type

    def set_pen_color(self, color):
        self.pen_color = QtGui.QColor(color)
        if self.tool == "marker":
            self.pen_color.setAlpha(self.marker_alpha)

    def set_pen_size(self, size):
        self.pen_size = size

    def set_background(self, type_):
        self.background_layer.fill(QtCore.Qt.GlobalColor.white)
        if type_ == "lines":
            painter = QtGui.QPainter(self.background_layer)
            pen = QtGui.QPen(QtGui.QColor("#666666"))
            painter.setPen(pen)
            for y in range(50, self.height(), 50):
                painter.drawLine(0, y, self.width(), y)
            painter.end()
        elif type_ == "grid":
            painter = QtGui.QPainter(self.background_layer)
            pen = QtGui.QPen(QtGui.QColor("#666666"))
            painter.setPen(pen)
            step = 50
            for y in range(0, self.height(), step):
                painter.drawLine(0, y, self.width(), y)
            for x in range(0, self.width(), step):
                painter.drawLine(x, 0, x, self.height())
            painter.end()
        self.update()


# --- Notebook class עם כמה דפים ---
class Notebook(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pages = QtWidgets.QStackedWidget()
        self.pages_list = []

        btn_prev = QtWidgets.QPushButton("Prev Page")
        btn_next = QtWidgets.QPushButton("Next Page")
        btn_add = QtWidgets.QPushButton("Add Page")

        btn_prev.clicked.connect(self.prev_page)
        btn_next.clicked.connect(self.next_page)
        btn_add.clicked.connect(self.add_page)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(btn_prev)
        top_layout.addWidget(btn_next)
        top_layout.addWidget(btn_add)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.pages)

        self.add_page()  # התחלה עם דף אחד

    def add_page(self):
        canvas = DrawingCanvas(START_WIDTH, START_HEIGHT)
        self.pages_list.append(canvas)
        self.pages.addWidget(canvas)
        self.pages.setCurrentWidget(canvas)

    def prev_page(self):
        index = self.pages.currentIndex()
        if index > 0:
            self.pages.setCurrentIndex(index - 1)

    def next_page(self):
        index = self.pages.currentIndex()
        if index < len(self.pages_list) - 1:
            self.pages.setCurrentIndex(index + 1)


# --- Main Window ---
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.notebook = Notebook()
        self.setCentralWidget(self.notebook)

        # כלים
        toolbar = QtWidgets.QToolBar("Tools")
        self.addToolBar(toolbar)

        for tool_name in ["pen", "marker", "eraser", "select"]:
            btn = QtWidgets.QPushButton(tool_name.capitalize())
            btn.clicked.connect(lambda checked, t=tool_name: self.set_tool(t))
            toolbar.addWidget(btn)

        # צבעים
        for color in COLORS:
            btn = QtWidgets.QPushButton()
            btn.setStyleSheet(f"background-color: {color}")
            btn.clicked.connect(lambda checked, c=color: self.set_color(c))
            toolbar.addWidget(btn)

        # גודל
        size_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        size_slider.setMinimum(1)
        size_slider.setMaximum(30)
        size_slider.setValue(5)
        size_slider.valueChanged.connect(self.set_size)
        toolbar.addWidget(size_slider)

        # רקע
        for bg in ["blank", "lines", "grid"]:
            btn = QtWidgets.QPushButton(bg.capitalize())
            btn.clicked.connect(lambda checked, b=bg: self.set_background(b))
            toolbar.addWidget(btn)

    def current_canvas(self):
        return self.notebook.pages.currentWidget()

    def set_tool(self, tool):
        self.current_canvas().set_tool(tool)

    def set_color(self, color):
        self.current_canvas().set_pen_color(color)

    def set_size(self, size):
        self.current_canvas().set_pen_size(size)

    def set_background(self, bg_type):
        self.current_canvas().set_background(bg_type)


# --- הפעלת האפליקציה ---
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
