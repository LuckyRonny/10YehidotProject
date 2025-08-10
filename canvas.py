"""
Ronny Getz
canvas and canvas container
"""

import math
import time
from style import *


class DrawingCanvas(QWidget):
    def __init__(self, width, height):
        super().__init__()
        # layers
        self.setFixedSize(width, height)
        self.background_layer = QtGui.QPixmap(self.size())
        self.background_layer.fill(Qt.GlobalColor.white)

        self.drawing_layer = QtGui.QPixmap(self.size())
        self.drawing_layer.fill(Qt.GlobalColor.transparent)

        # points and history
        self.history = []
        self.drawing = False
        self.last_point = QtCore.QPoint()
        self.first_point = QtCore.QPoint()
        self.points = []

        # type and color
        self.pen_color = "black"
        self.pen_size = 1
        self.tool = "pen"
        self.page_type = "blank"

        # zoom in
        self.is_gesturing = False
        self.last_pan_center = None
        self.grabGesture(QtCore.Qt.GestureType.PinchGesture)
        self.grabGesture(QtCore.Qt.GestureType.PanGesture)
        self.scale_factor = 1.0
        self.base_width = width
        self.base_height = height

    def paintEvent(self, event):
        """create the background and layers"""
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("#D3E9FF"))
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.drawPixmap(START_PIXMAP, START_PIXMAP, self.background_layer)
        painter.drawPixmap(START_PIXMAP, START_PIXMAP, self.drawing_layer)

    def mousePressEvent(self, event):
        """when mouse pressed change to drawing"""
        if self.is_gesturing:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.history.append(self.drawing_layer.copy())
            self.last_point = (event.position() / self.scale_factor).toPoint()
            self.first_point = (event.position() / self.scale_factor).toPoint()
            self.points = []

    def create_painter(self, pen_size, pen_color, layer):
        """create the painter with the right parameters"""
        painter = QtGui.QPainter(layer)
        pen = QtGui.QPen(QtGui.QColor(pen_color),
                         pen_size,
                         Qt.PenStyle.SolidLine,
                         Qt.PenCapStyle.RoundCap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(pen)
        return painter

    def mouseMoveEvent(self, event):
        """when mouse move and pressed creates
        a line from last point to current point"""
        if self.is_gesturing:
            return
        if self.drawing:
            current_point = (event.position() / self.scale_factor).toPoint()
            painter = self.create_painter(self.pen_size, self.pen_color,
                                          self.drawing_layer)
            if self.tool == "eraser":
                pen = QtGui.QPen(QtGui.QColor(*CLEAR_COLOR), self.pen_size)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setCompositionMode(
                    QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                painter.setPen(pen)
            painter.drawLine(self.last_point, current_point)
            painter.end()
            self.last_point = current_point
            self.points.append((self.last_point, time.time_ns()))
            self.update()

    @staticmethod
    def distance(point1, point2):
        """calculate distance"""
        return math.sqrt((point1.x() - point2.x()) ** SQUARED +
                         (point1.y() - point2.y()) ** SQUARED)

    @staticmethod
    def _are_last_points_close(point_list, close_points_distance,
                               close_points_time):
        """check if the points are close"""
        if len(point_list) == 0:
            return False
        current_time = time.time_ns()
        for point in point_list:
            if (current_time - point[TIME_OF_POINT_INDEX] < close_points_time
                    and DrawingCanvas.distance(point[POINT_INDEX],
                                           point_list[LAST_POINT][POINT_INDEX])
                    > close_points_distance):
                return False
        return True

    def mouseReleaseEvent(self, event):
        """when mouse released change to not drawing
        and check if it needs to straighten the line """
        if self.is_gesturing:
            return
        if (self.drawing is True and
                event.button() == Qt.MouseButton.LeftButton):
            self.drawing = False
            if not self.tool == "eraser":
                painter = self.create_painter(self.pen_size,
                                              self.pen_color,
                                              self.drawing_layer)
                painter.drawPoint(self.last_point)
                painter.end()
                if DrawingCanvas._are_last_points_close(self.points,
                                                        DrawingCanvas.distance(
                                                            self.last_point,
                                                            self.first_point) -
                                                        CLOSE_POINTS_DISTANCE,
                                                        CLOSE_POINTS_TIME):
                    self.draw_line()
            self.update()

    def history_push(self):
        """save the line before straitening"""
        before_line = self.drawing_layer.copy()
        self.back()
        self.history.append(self.drawing_layer.copy())
        self.history.append(before_line.copy())

    def draw_line(self):
        """draw the line from the first point to last"""
        self.history_push()
        painter = self.create_painter(self.pen_size,
                                      self.pen_color,
                                      self.drawing_layer)
        if self.tool == "marker":
            for i in range(MARKER_LINE_TIMES):
                painter.drawLine(self.first_point, self.last_point)
        painter.drawLine(self.first_point, self.last_point)
        painter.end()

    def clear_canvas(self):
        """cleans the canvas"""
        self.drawing_layer.fill(Qt.GlobalColor.transparent)
        self.update()

    def save_canvas(self):
        """Open a file dialog to save the canvas with a custom name"""
        result = self.combine_layers()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "drawing.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in [".png", ".jpg", ".jpeg"]:
                filename += ".png"

            result.save(filename)
            QMessageBox.information(self, "Saved",
                                    f"Saved to:\n{filename}")

    def combine_layers(self):
        """combine the layers"""
        result = QtGui.QPixmap(self.size())
        result.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(result)
        painter.drawPixmap(START_PIXMAP, START_PIXMAP, self.background_layer)
        painter.drawPixmap(START_PIXMAP, START_PIXMAP, self.drawing_layer)
        painter.end()
        return result

    def change_pen_size(self, size):
        """changes pen size"""
        self.pen_size = size / 2

    def set_tool(self, tool_type):
        """set the tool that is used"""
        self.tool = tool_type

    def change_pen_color(self, i):
        """changes pen size"""
        if self.tool == "marker":
            color = QtGui.QColor(MARKER_COLORS[i])
            color.setAlpha(50)
        else:
            color = QtGui.QColor(COLORS[i])
            color.setAlpha(255)
        self.pen_color = color

    def back(self):
        """changes pen size"""
        if self.history:
            self.drawing_layer = self.history.pop()
            self.update()

    def zoom_in(self):
        """change the scale factor *1.2"""
        self.scale_factor *= SCALE_CHANGE
        self.scale_factor = max(SCALE_MIN,
                                min(SCALE_MAX, self.scale_factor))
        self._update_size()

    def zoom_out(self):
        """change the scale factor /1.2"""
        self.scale_factor /= SCALE_CHANGE
        self.scale_factor = max(SCALE_MIN,
                                min(SCALE_MAX, self.scale_factor))
        self._update_size()

    def _update_size(self):
        """change the size of the canvas by the scale factor"""
        new_width = int(self.base_width * self.scale_factor)
        new_height = int(self.base_height * self.scale_factor)
        self.setFixedSize(new_width, new_height)
        self.update()

    def event(self, event):
        """check if the event is gesture"""
        if event.type() == QtCore.QEvent.Type.Gesture:
            return self.gesture_event(event)
        return super().event(event)

    def gesture_event(self, event):
        """check if zoom or slide"""
        pinch = event.gesture(QtCore.Qt.GestureType.PinchGesture)
        if pinch:
            self.is_gesturing = True
            self.handle_pinch(pinch)
            if pinch.state() == Qt.GestureState.GestureFinished:
                self.is_gesturing = False
            return True
        pan = event.gesture(QtCore.Qt.GestureType.PanGesture)
        if pan:
            self.is_gesturing = True
            if pan.state() == Qt.GestureState.GestureFinished:
                self.is_gesturing = False
            return True
        return False

    def handle_pinch(self, pinch):
        """handle zoom in"""
        if pinch.state() == Qt.GestureState.GestureUpdated:
            scale_change = pinch.scaleFactor()
            self.scale_factor *= scale_change
            self.scale_factor = max(SCALE_MIN,
                                    min(SCALE_MAX, self.scale_factor))
            self._update_size()
            self.update()

    def blank(self):
        """change the canvas to be blank"""
        self.page_type = "blank"
        self.background_layer.fill(Qt.GlobalColor.white)
        self.update()

    def lines(self):
        """change the back to be lines"""
        self.page_type = "lines"
        self.background_layer.fill(Qt.GlobalColor.white)
        painter = self.create_painter(BACKGROUND_PEN_SIZE, "#666666",
                                      self.background_layer)
        start = START_LINE
        end = END_LINE
        n_lines = NUMBER_LINES
        step_size = int((end - start)/n_lines)
        for i in range(start, end, step_size):
            row_start, row_end = ROW_LIMITS
            painter.drawLine(row_start, i, row_end, i)
        painter.drawLine(*RIGHT_LINE)
        painter.end()
        painter = self.create_painter(BACKGROUND_PEN_SIZE, "#CCCCCC",
                                      self.background_layer)
        painter.drawLine(*LEFT_LINE)
        painter.end()
        self.update()

    def grid(self):
        """change the back to be grid"""
        self.page_type = "grid"
        self.background_layer.fill(Qt.GlobalColor.white)
        painter = self.create_painter(BACKGROUND_PEN_SIZE, "#666666",
                                      self.background_layer)
        start = START_GRID
        end = END_GRID[ROW_INDEX]
        n_lines = NUMBER_LINES_GRID
        step_size = int((end - start) / n_lines)
        for i in range(start, end, step_size):
            row_start, row_end = ROW_LIMITS
            painter.drawLine(row_start, i, row_end, i)
        end = END_GRID[COLUMN_INDEX]
        for i in range(start, end, step_size):
            column_start, column_end = COLUMN_LIMITS
            painter.drawLine(i, column_start, i, column_end)
        painter.end()
        self.update()


class CanvasContainer(QWidget):
    def __init__(self, child_widget):
        super().__init__()
        self.child_widget = child_widget

        layout = QVBoxLayout()
        layout.addStretch(1)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.child_widget)
        h_layout.addStretch(1)

        layout.addLayout(h_layout)
        layout.addStretch(1)
        self.setLayout(layout)

    def paintEvent(self, event):
        """draw the background"""
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("#D3E9FF"))


class CenteredScrollArea(QScrollArea):
    def __init__(self, canvas_widget):
        super().__init__()
        self.canvas_widget = canvas_widget
        self.setWidgetResizable(True)

        container = CanvasContainer(canvas_widget)

        self.setWidget(container)

    def wheelEvent(self, event):
        """check if zoom in or out"""
        if (QApplication.keyboardModifiers() ==
                Qt.KeyboardModifier.ControlModifier):
            if event.angleDelta().y() > 0:
                self.canvas_widget.zoom_in()
            else:
                self.canvas_widget.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
