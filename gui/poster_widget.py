from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt, Signal
import os

class PosterWidget(QWidget):
    clicked = Signal()

    def __init__(self, image_filename, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedSize(220, 360)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "assets", image_filename)

        self.image_label = QLabel()
        pixmap = QPixmap(image_path).scaled(
            200, 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.image_label)
        layout.addWidget(self.title_label)
        self.setLayout(layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
