from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QVBoxLayout
from PyQt6.QtGui import QPixmap, QColor, QPalette
from PyQt6.QtCore import Qt
import sys


class PixmapWithTransparentText(QWidget):
    def __init__(self):
        super().__init__()

        # Label for pixmap
        self.pixmap_label = QLabel(self)
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("lightblue"))  # Fill with background color
        self.pixmap_label.setPixmap(pixmap)

        # Transparent QTextEdit
        self.text_edit = QTextEdit(self)
        self.text_edit.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: black;
                font-size: 16px;
            }
        """)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Layout (stacked manually by positioning)
        self.pixmap_label.setGeometry(0, 0, 400, 300)
        self.text_edit.setGeometry(0, 0, 400, 300)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PixmapWithTransparentText()
    window.setWindowTitle("Pixmap + Transparent TextEdit")
    window.setFixedSize(400, 300)
    window.show()
    sys.exit(app.exec())
