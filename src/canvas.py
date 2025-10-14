"""
Ronny Getz
canvas and canvas container
"""

import math
import random
import time
from style import *


class Stroke(object):
    def __init__(self, points, pen_color, pen_size):
        self.points = points
        self.pen_color = pen_color
        self.pen_size = pen_size
        self.selected = False

    def contains_point(self, pt, tolerance):
        for i in range(SECOND_POINT, len(self.points)):
            p1, p2 = self.points[i-POINT_BEFORE], self.points[i]
            if self.point_line_distance(pt, p1, p2) <= tolerance:
                return True
        return False

    @staticmethod
    def point_line_distance(p, a, b):
        """Return the minimum distance from point p to line segment ab"""
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        px, py = p.x(), p.y()
        dx, dy = bx - ax, by - ay
        if dx == dy == SAME_POINT:
            return ((px - ax)**SQUARED + (py - ay)**SQUARED) ** SQUARE_ROOT
        t = max(LINE_POINT_START,
                min(LINE_POINT_END,
                    ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
        closest_x = ax + t*dx
        closest_y = ay + t*dy
        return (((px - closest_x)**SQUARED + (py - closest_y)**SQUARED) **
                SQUARE_ROOT)


class DrawingCanvas(QWidget):
    def __init__(self, width, height):
        super().__init__()
        # layers
        self.setFixedSize(width, height)
        self.background_layer = QtGui.QPixmap(self.size())
        self.background_layer.fill(Qt.GlobalColor.white)

        # Add strokes
        self.strokes = []
        self.current_stroke_points = []

        # For moving strokes
        self.selected_stroke = None
        self.drawing = False

        # points and history
        self.history = []
        self.drawing = False
        self.last_point = QtCore.QPoint()
        self.first_point = QtCore.QPoint()
        self.points = []

        # type and color
        self.pen_color = QtGui.QColor("black")
        self.pen_size = PEN_START_VALUE / PEN_SIZE_FACTOR
        self.tool = "pen"
        self.page_type = "blank"

        # zoom in
        self.is_gesturing = False
        self.last_pan_center = None
        self.grabGesture(QtCore.Qt.GestureType.PinchGesture)
        self.grabGesture(QtCore.Qt.GestureType.PanGesture)
        self.scale_factor = START_SCALE_FACTOR
        self.base_width = width
        self.base_height = height

    def paintEvent(self, event):
        """create the background and layers"""
        try:
            painter = QtGui.QPainter(self)
            painter.fillRect(self.rect(), QtGui.QColor("#D3E9FF"))
            painter.setRenderHint(
                QtGui.QPainter.RenderHint.SmoothPixmapTransform)

            painter.save()
            painter.scale(self.scale_factor, self.scale_factor)
            painter.drawPixmap(START_PIXMAP, START_PIXMAP,
                               self.background_layer)
            painter.restore()

            painter.save()
            painter.scale(self.scale_factor, self.scale_factor)
            for stroke in self.strokes:
                pen = self.create_pen(stroke.pen_size, stroke.pen_color)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                painter.setPen(pen)
                pts = stroke.points
                if len(pts) > 1:
                    for i in range(SECOND_POINT, len(pts)):
                        painter.drawLine(pts[i - 1], pts[i])
                if stroke.selected:
                    highlight = self.create_pen(stroke.pen_size + 1,
                                                stroke.pen_color.lighter(130))
                    painter.setPen(highlight)
                    for i in range(SECOND_POINT, len(pts)):
                        painter.drawLine(pts[i - 1], pts[i])

            # Draw the stroke being currently drawn
            if self.drawing and len(self.current_stroke_points) > 1:
                pen = self.create_pen(self.pen_size,
                                      QtGui.QColor(self.pen_color))
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                painter.setPen(pen)
                pts = self.current_stroke_points
                for i in range(SECOND_POINT, len(pts)):
                    painter.drawLine(pts[i - 1], pts[i])

            painter.restore()
        except Exception as e:
            print("paintEvent crash:", e)
            return

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = (event.position() / self.scale_factor).toPoint()

            if self.tool in ["pen", "marker"]:
                self.drawing = True
                self.current_stroke_points = [pos]
            elif self.tool == "select":
                self.selected_stroke = None
                for stroke in reversed(self.strokes):
                    if stroke.contains_point(pos, tolerance=2):
                        stroke.selected = True
                        self.selected_stroke = stroke
                        self.last_point = pos  # important for movement
                        break
                    else:
                        stroke.selected = False
                self.update()
            elif self.tool == "eraser":
                # erase immediately when clicking
                new_strokes = [
                    s for s in self.strokes
                    if not s.contains_point(pos, tolerance=self.pen_size * 1.5)
                ]
                self.strokes = new_strokes
                self.update()

    def create_pen(self, pen_size, pen_color):
        """create the painter with the right parameters"""
        pen = QtGui.QPen(QtGui.QColor(pen_color),
                         pen_size,
                         Qt.PenStyle.SolidLine,
                         Qt.PenCapStyle.RoundCap)
        return pen

    def mouseMoveEvent(self, event):
        """when mouse move and pressed creates
        a line from last point to current point"""
        if self.is_gesturing:
            return
        pos = (event.position() / self.scale_factor).toPoint()
        if self.move_selected_stroke(event, pos):
            return
        if self.drawing:
            if (self.tool == "eraser" and event.buttons() &
                  QtCore.Qt.MouseButton.LeftButton):
                self.current_stroke_points.append(pos)
                self.erase_points(pos)
                self.update()
            elif self.tool in ["pen", "marker"] and self.drawing:
                self.current_stroke_points.append(pos)
                self.update()

    def move_selected_stroke(self, e, pos):
        if (self.tool == "select" and self.selected_stroke and
                e.buttons() & QtCore.Qt.MouseButton.LeftButton):
            dx = pos.x() - self.last_point.x()
            dy = pos.y() - self.last_point.y()
            self.selected_stroke.points = [QtCore.QPoint(p.x() + dx, p.y() + dy)
                                           for p in self.selected_stroke.points]
            self.last_point = pos
            self.update()
            return True
        return False

    def erase_points(self, pos):
        """Erase only the part of strokes that are under the eraser"""
        erase_radius = self.pen_size * 1.5
        new_strokes = []

        for stroke in self.strokes:
            if len(stroke.points) < 2:
                continue

            new_segments = []
            segment = []

            for i in range(len(stroke.points) - 1):
                p1 = stroke.points[i]
                p2 = stroke.points[i + 1]
                if Stroke.point_line_distance(pos, p1, p2) > erase_radius:
                    segment.append(p1)
                else:
                    if len(segment) > 1:
                        new_segments.append(segment[:])
                    segment = []
            if len(segment) > 1:
                new_segments.append(segment)

            for seg in new_segments:
                new_strokes.append(
                    Stroke(seg, stroke.pen_color, stroke.pen_size))

        self.strokes = new_strokes

    @staticmethod
    def distance(point1, point2):
        """calculate distance"""
        return math.sqrt((point1.x() - point2.x()) ** SQUARED +
                         (point1.y() - point2.y()) ** SQUARED)

    @staticmethod
    def _are_last_points_close(point_list, close_points_distance,
                               close_points_time):
        """check if the points are close"""
        if len(point_list) == EMPTY_POINT_LIST:
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
        pos = (event.position() / self.scale_factor).toPoint()

        if self.tool in ["pen", "marker"] and self.drawing:
            self.drawing = False
            stroke = Stroke(
                points=self.current_stroke_points[:],
                pen_color=self.pen_color,
                pen_size=self.pen_size
            )
            self.strokes.append(stroke)
            self.current_stroke_points = []
            self.update()
        elif self.tool == "select":
            if self.selected_stroke:
                self.selected_stroke.selected = False
                self.selected_stroke = None
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
        self.strokes = []
        self.current_stroke_points = []
        self.selected_stroke = None
        self.update()

    def save_canvas(self):
        """Open a file dialog to save the canvas with a custom name"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Image", "drawing.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        if not filename:
            return

        result = QtGui.QPixmap(self.size())
        result.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(result)
        painter.drawPixmap(START_PIXMAP, START_PIXMAP, self.background_layer)
        for stroke in self.strokes:
            pen = QtGui.QPen(stroke.pen_color, stroke.pen_size)
            painter.setPen(pen)
            pts = stroke.points
            if len(pts) > 1:
                for i in range(SECOND_POINT, len(pts)):
                    painter.drawLine(pts[i - POINT_BEFORE], pts[i])
        painter.end()

        ext = filename.split(".")[-1].lower()
        if ext not in ["png", "jpg", "jpeg"]:
            filename += ".png"
        result.save(filename)
        QtWidgets.QMessageBox.information(self, "Saved",
                                          f"Saved to:\n{filename}")

    def set_tool(self, tool_type):
        """set the tool that is used"""
        self.tool = tool_type

    def change_pen_size(self, size):
        """changes pen size"""
        if self.tool == "pen":
            self.pen_size = size / PEN_SIZE_FACTOR
        else:
            self.pen_size = size

    def change_pen_color(self, i):
        """changes pen size"""
        if self.tool == "marker":
            color = QtGui.QColor(MARKER_COLORS[i])
            color.setAlpha(TRANSPARENCY_MARKER)
        else:
            color = QtGui.QColor(COLORS[i])
            color.setAlpha(TRANSPARENCY_PEN)
        self.pen_color = color

    def back(self):
        if self.strokes:
            self.strokes.pop()
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
        painter = QtGui.QPainter(self.background_layer)
        pen = self.create_pen(BACKGROUND_PEN_SIZE, "#666666")
        painter.setPen(pen)
        start = START_LINE
        end = END_LINE
        n_lines = NUMBER_LINES
        step_size = int((end - start)/n_lines)
        for i in range(start, end, step_size):
            row_start, row_end = ROW_LIMITS
            painter.drawLine(row_start, i, row_end, i)
        painter.drawLine(*RIGHT_LINE)
        painter.end()
        painter = QtGui.QPainter(self.background_layer)
        pen = self.create_pen(BACKGROUND_PEN_SIZE, "#666666")
        painter.setPen(pen)
        painter.drawLine(*LEFT_LINE)
        painter.end()
        self.update()

    def grid(self):
        """change the back to be grid"""
        self.page_type = "grid"
        self.background_layer.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(self.background_layer)
        pen = self.create_pen(BACKGROUND_PEN_SIZE, "#666666")
        painter.setPen(pen)
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
        layout.addStretch(STRETCH)

        h_layout = QHBoxLayout()
        h_layout.addStretch(STRETCH)
        h_layout.addWidget(self.child_widget)
        h_layout.addStretch(STRETCH)

        layout.addLayout(h_layout)
        layout.addStretch(STRETCH)
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
            if event.angleDelta().y() > START_ANGLE:
                self.canvas_widget.zoom_in()
            else:
                self.canvas_widget.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
