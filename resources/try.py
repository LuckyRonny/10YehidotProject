import sys
from PyQt6 import QtCore, QtGui, QtWidgets


class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.image = QtGui.QPixmap(800, 600)
        self.image.fill(QtCore.Qt.GlobalColor.white)
        self.setPixmap(self.image)

        self.drawing = False
        self.last_point = QtCore.QPoint()
        self.mode = "draw"

        self.text_edit = None
        self.toolbar = None

    def set_mode(self, mode):
        if mode == "text":
            self.start_text_mode()
        elif mode == "draw":
            self.commit_text_to_pixmap()
        self.mode = mode

    def start_text_mode(self):
        if not self.text_edit:
            self.text_edit = QtWidgets.QTextEdit(self)
            self.text_edit.setGeometry(self.rect())
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background: transparent;
                    border: none;
                    color: black;
                }
            """)
            self.text_edit.setFontPointSize(16)
            self.text_edit.show()
            self.create_toolbar()

    def create_toolbar(self):
        if self.toolbar:
            self.toolbar.deleteLater()

        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        self.toolbar.setMovable(False)

        # Bold
        bold_action = QtGui.QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(
            lambda: self.toggle_format("bold", bold_action.isChecked()))
        self.toolbar.addAction(bold_action)

        # Italic
        italic_action = QtGui.QAction("I", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(
            lambda: self.toggle_format("italic", italic_action.isChecked()))
        self.toolbar.addAction(italic_action)

        # Underline
        underline_action = QtGui.QAction("U", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(
            lambda: self.toggle_format("underline", underline_action.isChecked()))
        self.toolbar.addAction(underline_action)

        # Font size
        size_box = QtWidgets.QComboBox(self.toolbar)
        for size in [8, 10, 12, 14, 16, 18, 20, 24, 28, 32]:
            size_box.addItem(str(size))
        size_box.setCurrentText("16")
        size_box.currentTextChanged.connect(
            lambda s: self.text_edit.setFontPointSize(float(s)))
        self.toolbar.addWidget(size_box)

        # Font color
        color_btn = QtWidgets.QPushButton("Color")
        color_btn.clicked.connect(self.choose_color)
        self.toolbar.addWidget(color_btn)

        self.toolbar.move(10, 10)
        self.toolbar.show()

    def toggle_format(self, fmt_type, enable):
        cursor = self.text_edit.textCursor()
        fmt = cursor.charFormat()
        if fmt_type == "bold":
            fmt.setFontWeight(QtGui.QFont.Weight.Bold if enable else QtGui.QFont.Weight.Normal)
        elif fmt_type == "italic":
            fmt.setFontItalic(enable)
        elif fmt_type == "underline":
            fmt.setFontUnderline(enable)
        cursor.mergeCharFormat(fmt)

    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            fmt = cursor.charFormat()
            fmt.setForeground(color)
            cursor.mergeCharFormat(fmt)

    def commit_text_to_pixmap(self):
        if self.text_edit:
            painter = QtGui.QPainter(self.image)
            self.text_edit.render(painter)
            painter.end()
            self.setPixmap(self.image)
            self.text_edit.deleteLater()
            self.text_edit = None
        if self.toolbar:
            self.toolbar.deleteLater()
            self.toolbar = None

    def mousePressEvent(self, event):
        if self.mode == "draw" and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.mode == "draw" and self.drawing:
            painter = QtGui.QPainter(self.image)
            pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 2)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            painter.end()
            self.setPixmap(self.image)
            self.last_point = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        if self.mode == "draw" and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.drawing = False


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        toolbar = self.addToolBar("Main")
        draw_action = QtGui.QAction("Draw", self)
        draw_action.triggered.connect(lambda: self.canvas.set_mode("draw"))
        toolbar.addAction(draw_action)

        text_action = QtGui.QAction("Text", self)
        text_action.triggered.connect(lambda: self.canvas.set_mode("text"))
        toolbar.addAction(text_action)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
