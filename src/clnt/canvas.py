"""
Ronny Getz
canvas
"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import math
import time
from stroke import *


class DrawingCanvas(QWidget):
    def __init__(self, width, height, strokes, page_type, notebook_area):
        """constructor"""
        super().__init__()
        # background layer
        self.create_background_layer(width, height)
        # Add strokes
        self.create_strokes_params(strokes)
        # points and history
        self.create_history_params()
        # type and color
        self.create_pen_params(page_type)
        # zoom in
        self.create_zoom_in_params(width, height)
        self.notebook_area = notebook_area

    def __dict__(self):
        """convert canvas to dictionary"""
        strokes_l = []
        for s in self.strokes:
            strokes_l.append(s.__dict__())
        canvas_dict = {
            "width": self.base_width,
            "height": self.base_height,
            "strokes": strokes_l,
            "page_type": self.page_type
        }
        return canvas_dict

    def create_background_layer(self, width, height):
        """create background layer"""
        self.setFixedSize(width, height)
        self.background_layer = QtGui.QPixmap(self.size())
        self.background_layer.fill(Qt.GlobalColor.white)

    def create_strokes_params(self, strokes):
        """create strokes parameters"""
        self.strokes = []
        if strokes:
            for s in strokes:
                self.strokes.append(Stroke(**s))
        self.current_stroke_points = []
        self.current_stroke_times = []
        self.selected_stroke = None
        self.drawing = False

    def create_history_params(self):
        """create history parameters"""
        self.history = []
        self.drawing = False
        self.last_point = QtCore.QPoint()
        self.first_point = QtCore.QPoint()

    def create_pen_params(self, page_type):
        """create pen parameters"""
        self.pen_color = QtGui.QColor("black")
        self.pen_size = PEN_START_VALUE / PEN_SIZE_FACTOR
        self.tool = "pen"
        self.page_type = page_type
        if page_type == "grid":
            self.grid()
        elif page_type == "lines":
            self.lines()
        else:
            self.blank()

    def create_zoom_in_params(self, width, height):
        """creates parameters for zoom in"""
        self.is_gesturing = False
        self.grabGesture(QtCore.Qt.GestureType.PinchGesture)
        self.scale_factor = START_SCALE_FACTOR
        self.base_width = width
        self.base_height = height

    def paintEvent(self, event):
        """create the background and draw every stroke in the canvas"""
        try:
            painter = QtGui.QPainter(self)
            self.draw_background(painter)
            painter.restore()
            painter.save()
            self.draw_strokes(painter)
            # Draw the stroke being currently drawn
            if (self.drawing and
                    len(self.current_stroke_points) > ONLY_ONE_POINT):
                self.draw_current_stroke(painter)
            painter.restore()
            if self.notebook_area:
                self.notebook_area.save_notebook()
        except Exception as e:
            print("paintEvent crash:", e)
            return

    def draw_strokes(self, painter):
        """draws all the strokes in the canvas"""
        for stroke in self.strokes:
            pen = self.create_pen(stroke.pen_size, stroke.pen_color)
            painter.setPen(pen)
            self.draw_stroke(stroke, painter)
            if stroke.selected:
                highlight = self.create_pen(stroke.pen_size +
                                            ADD_SELECTED_PEN_SIZE,
                                            stroke.pen_color.lighter(
                                                LIGHTER_COLOR))
                painter.setPen(highlight)
                self.draw_stroke(stroke, painter)

    def draw_background(self, painter):
        """draw the background"""
        painter.fillRect(self.rect(), QtGui.QColor("#D3E9FF"))
        painter.setRenderHint(
            QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.save()
        painter.drawPixmap(START_PIXMAP, START_PIXMAP,
                           self.background_layer)

    def draw_current_stroke(self, painter):
        """draw the current stroke"""
        pen = self.create_pen(self.pen_size,
                              QtGui.QColor(self.pen_color))
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(pen)
        pts = self.current_stroke_points
        for i in range(SECOND_POINT, len(pts)):
            painter.drawLine(pts[i - POINT_BEFORE], pts[i])

    def draw_stroke(self, stroke, painter):
        """draws a stroke"""
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        pts = stroke.points
        if len(pts) > ONLY_ONE_POINT:
            for i in range(SECOND_POINT, len(pts)):
                painter.drawLine(pts[i - POINT_BEFORE], pts[i])

    def mousePressEvent(self, event):
        """when mouse pressed check which tool is used
        and set the correct parameters"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = (event.position() / self.scale_factor).toPoint()
            if self.tool in ["pen", "marker"]:
                self.drawing = True
                self.current_stroke_points = [pos]
                self.current_stroke_times = [time.time_ns()]
            elif self.tool == "select":
                self.selected_stroke = None
                self.check_which_selected(pos)
                self.update()
            elif self.tool == "eraser":
                # erase immediately when clicking
                new_strokes = []
                for s in self.strokes:
                    if not s.contains_point(pos,
                                            self.pen_size * ERASER_TOLERANCE):
                        new_strokes.append(s)
                self.strokes = new_strokes
                self.update()

    def check_which_selected(self, pos):
        """check which stroke is selected from the end"""
        for stroke in reversed(self.strokes):
            if stroke.contains_point(pos,
                                     stroke.pen_size /
                                     SELECTED_TOLERANCE):
                stroke.selected = True
                self.selected_stroke = stroke
                self.last_point = pos  # important for movement
                break
            else:
                stroke.selected = False

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
            if self.tool in ["pen", "marker"]:
                self.current_stroke_points.append(pos)
                self.current_stroke_times.append(time.time_ns())
                self.update()

    def move_selected_stroke(self, e, pos):
        """change the location of the stroke to the wanted location"""
        if (self.tool == "select" and self.selected_stroke and
                e.buttons() & QtCore.Qt.MouseButton.LeftButton):
            dx = pos.x() - self.last_point.x()
            dy = pos.y() - self.last_point.y()
            select_points = self.selected_stroke.points
            self.selected_stroke.points = []
            for p in select_points:
                new_p = QtCore.QPoint(p.x() + dx, p.y() + dy)
                self.selected_stroke.points.append(new_p)
            self.last_point = pos
            self.update()
            return True
        return False

    @staticmethod
    def distance(point1, point2):
        """calculate distance"""
        return math.sqrt((point1.x() - point2.x()) ** SQUARED +
                         (point1.y() - point2.y()) ** SQUARED)

    @staticmethod
    def _are_last_points_close(point_list, time_list, close_points_distance,
                               close_points_time):
        """check if the points are close"""
        if len(point_list) == EMPTY_POINT_LIST:
            return False
        current_time = time.time_ns()
        for i in range(len(point_list)):
            if (current_time - time_list[i] <
                    close_points_time and
                    DrawingCanvas.distance(point_list[i],
                                           point_list[LAST_POINT]) >
                    close_points_distance):
                return False
        return True

    def mouseReleaseEvent(self, event):
        """when mouse released resset the tool
        and check if it needs to straighten the line """
        if self.is_gesturing:
            return
        if self.current_stroke_points:
            start_to_end = DrawingCanvas.distance(
                self.current_stroke_points[STROKE_POINT_START],
                self.current_stroke_points[STROKE_POINT_END])
            if (self.drawing and DrawingCanvas._are_last_points_close(
                    self.current_stroke_points, self.current_stroke_times,
                    start_to_end / CLOSE_POINTS_DISTANCE, CLOSE_POINTS_TIME)):
                self.create_straight_line()
            elif self.tool in ["pen", "marker"] and self.drawing:
                self.end_stroke()
        elif self.tool == "select":
            if self.selected_stroke:
                self.selected_stroke.selected = False
                self.selected_stroke = None
            self.update()

    def create_straight_line(self):
        """create a straight line and resset the parameters"""
        new_stroke = Stroke(
            [self.current_stroke_points[STROKE_POINT_START],
                self.current_stroke_points[STROKE_POINT_END]],
            [self.current_stroke_times[STROKE_POINT_START],
                self.current_stroke_times[STROKE_POINT_END]],
            self.pen_color, self.pen_size)
        self.strokes.append(new_stroke)
        self.current_stroke_points = []
        self.current_stroke_times = []
        self.update()

    def end_stroke(self):
        """add the stroke and resset the parameters"""
        stroke = Stroke(self.current_stroke_points[:],
                        self.current_stroke_times,
                        self.pen_color, self.pen_size)
        self.drawing = False
        self.strokes.append(stroke)
        self.current_stroke_points = []
        self.current_stroke_times = []
        self.update()

    def clear_canvas(self):
        """cleans the canvas"""
        self.history = self.strokes
        self.strokes = []
        self.current_stroke_points = []
        self.selected_stroke = None
        self.update()

    def draw_all_canvas(self):
        """ draws all the canvas"""
        scale_factor = self.scale_factor
        self.scale_factor = START_SCALE_FACTOR
        self._update_size()
        self.update()
        result = QtGui.QPixmap(self.size())
        result.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(result)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.drawPixmap(START_PIXMAP, START_PIXMAP, self.background_layer)
        for stroke in self.strokes:
            pen = self.create_pen(stroke.pen_size, stroke.pen_color)
            painter.setPen(pen)
            self.draw_stroke(stroke, painter)
        painter.end()
        self.scale_factor = scale_factor
        self._update_size()
        self.update()
        return result

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
        """remove the last stroke or if empty get history"""
        if self.strokes:
            self.strokes.pop()
            self.update()
        else:
            self.strokes = self.history
            self.history = []
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
        return False

    def handle_pinch(self, pinch):
        """change the scale factor and update the size of the canvas"""
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
