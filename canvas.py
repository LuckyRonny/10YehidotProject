from style import *


class DrawingCanvas(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        self.background_layer = QtGui.QPixmap(self.size())
        self.background_layer.fill(Qt.GlobalColor.white)

        self.drawing_layer = QtGui.QPixmap(self.size())
        self.drawing_layer.fill(Qt.GlobalColor.transparent)

        self.history = []
        self.drawing = False
        self.last_point = QtCore.QPoint()

        self.pen_color = "black"
        self.pen_size = 1
        self.tool = "pen"
        self.page_type = "blank"

        self.scale_factor = 1.0
        self.base_width = width
        self.base_height = height

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setTransform(QtGui.QTransform())
        painter.fillRect(self.rect(), QtGui.QColor("#D3E9FF"))
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.drawPixmap(0, 0, self.background_layer)
        painter.drawPixmap(0, 0, self.drawing_layer)

    def mousePressEvent(self, event):
        """when mouse pressed change to drawing"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.history.append(self.drawing_layer.copy())
            self.last_point = (event.position() / self.scale_factor).toPoint()

    def create_painter(self, pen_size, pen_color, layer):
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
        if self.drawing:
            current_point = (event.position() / self.scale_factor).toPoint()
            painter = self.create_painter(self.pen_size, self.pen_color,
                                          self.drawing_layer)
            if self.tool == "eraser":
                pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), self.pen_size)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setCompositionMode(
                    QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                painter.setPen(pen)
            painter.drawLine(self.last_point, current_point)
            painter.end()
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        """when mouse released change to not drawing"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def clear_canvas(self):
        """cleans the canvas"""
        self.drawing_layer.fill(Qt.GlobalColor.transparent)
        self.update()

    def save_canvas(self):
        """Open a file dialog to save the canvas with a custom name"""
        result = QtGui.QPixmap(self.size())
        result.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(result)
        painter.drawPixmap(0, 0, self.background_layer)
        painter.drawPixmap(0, 0, self.drawing_layer)
        painter.end()
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
            color.setAlpha(30)
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
        self.scale_factor *= 1.2
        self._update_size()

    def zoom_out(self):
        self.scale_factor /= 1.2
        self._update_size()

    def reset_zoom(self):
        self.scale_factor = 1.0
        self._update_size()

    def _update_size(self):
        new_width = int(self.base_width * self.scale_factor)
        new_height = int(self.base_height * self.scale_factor)
        self.setFixedSize(new_width, new_height)
        self.update()

    def blank(self):
        self.page_type = "blank"
        self.background_layer.fill(Qt.GlobalColor.white)
        self.update()

    def lines(self):
        self.page_type = "lines"
        self.background_layer.fill(Qt.GlobalColor.white)
        painter = self.create_painter(0.5, "#666666",
                                      self.background_layer)
        start = 50
        end = 700
        n_lines = 30
        step_size = int((end - start)/n_lines)
        for i in range(start, end, step_size):
            painter.drawLine(0, i, 550, i)
        painter.drawLine(500, 0, 500, 700)
        painter.end()
        painter = self.create_painter(0.5, "#CCCCCC",
                                      self.background_layer)
        painter.drawLine(50, 0, 50, 700)
        painter.end()
        self.update()

    def grid(self):
        self.page_type = "grid"
        self.background_layer.fill(Qt.GlobalColor.white)
        painter = self.create_painter(0.5, "#666666",
                                      self.background_layer)
        start = 0
        end = 700
        n_lines = 45
        step_size = int((end - start) / n_lines)
        for i in range(start, end, step_size):
            painter.drawLine(0, i, 550, i)
        end = 550
        for i in range(start, end, step_size):
            painter.drawLine(i, 0, i, 700)
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
        if (QApplication.keyboardModifiers() ==
                Qt.KeyboardModifier.ControlModifier):
            if event.angleDelta().y() > 0:
                self.canvas_widget.zoom_in()
            else:
                self.canvas_widget.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

