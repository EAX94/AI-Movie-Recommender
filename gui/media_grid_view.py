from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QScrollArea, QSizePolicy, QPushButton, QHBoxLayout, QLineEdit, QComboBox
from PySide6.QtGui import QPixmap, QIcon, QImage
from PySide6.QtCore import Qt, QSize, Signal, QThreadPool, QRunnable, QObject, Slot
from pathlib import Path
import pandas as pd
import os
from PIL import Image
import io
from src.config import METADATA_PATH

PROJECT_ROOT = Path(__file__).resolve().parents[1]

class ImageLoadedSignal(QObject):
    loaded = Signal(QImage, object)

class ImageLoader(QRunnable):
    def __init__(self, image_path, label, signal):
        super().__init__()
        self.image_path = image_path
        self.label = label
        self.signal = signal

    @Slot()
    def run(self):
        try:
            with Image.open(self.image_path) as img:
                img = img.convert("RGBA")
                img = img.resize((120, 180), Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                qimage = QImage.fromData(buffer.getvalue(), "PNG")
                self.signal.loaded.emit(qimage, self.label)
        except Exception as e:
            print(f"Failed to load image {self.image_path}: {e}")

class MediaGridView(QWidget):
    poster_clicked = Signal(dict)
    back_clicked = Signal()

    def __init__(self, media_type, parent=None):
        super().__init__(parent)
        self.media_type = media_type
        self.df = pd.read_csv(METADATA_PATH)
        self.filtered = self.df[self.df["media_type"] == self.media_type].reset_index(drop=True)
        self.loaded_items = 0
        self.batch_size = 25
        self.active_genre = None
        self.search_query = ""

        self.threadpool = QThreadPool()
        self.image_signal = ImageLoadedSignal()
        self.image_signal.loaded.connect(self.set_poster_image)

        self.layout = QVBoxLayout(self)

        # Top bar
        top_bar = QHBoxLayout()

        self.back_button = QPushButton()
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "back_arrow.png")
        if os.path.exists(icon_path):
            self.back_button.setIcon(QIcon(icon_path))
        else:
            self.back_button.setText("\u2190 Back")
        self.back_button.setFixedSize(80, 30)
        self.back_button.clicked.connect(self.back_clicked.emit)
        top_bar.addWidget(self.back_button)
        top_bar.addSpacing(10)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setMinimumWidth(300)
        self.search_bar.textChanged.connect(self.apply_filters)
        top_bar.addWidget(self.search_bar, stretch=2)
        top_bar.addSpacing(10)

        self.genre_filter = QComboBox()
        all_genres = sorted(set(g for sub in self.filtered["genres"].dropna() for g in str(sub).split(", ")))
        self.genre_filter.addItem("All Genres")
        for genre in all_genres:
            self.genre_filter.addItem(genre)
        self.genre_filter.currentTextChanged.connect(self.apply_filters)
        top_bar.addWidget(self.genre_filter)

        self.layout.addLayout(top_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.verticalScrollBar().valueChanged.connect(self.on_scroll)

        self.container = QWidget()
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(20)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.container.setLayout(self.grid)
        self.scroll.setWidget(self.container)

        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)

        self.populate_grid()

    def apply_filters(self):
        self.search_query = self.search_bar.text().lower().strip()
        self.active_genre = self.genre_filter.currentText()

        filtered = self.df[self.df["media_type"] == self.media_type]

        if self.search_query:
            filtered = filtered[filtered["title"].str.lower().str.contains(self.search_query, na=False)]

        if self.active_genre and self.active_genre != "All Genres":
            filtered = filtered[filtered["genres"].str.contains(self.active_genre, na=False)]

        self.filtered = filtered.reset_index(drop=True)
        self.reload_grid()

    def populate_grid(self):
        columns = max(self.width() // 180, 1)

        for index in range(self.loaded_items, min(self.loaded_items + self.batch_size, len(self.filtered))):
            col = index % columns
            row_pos = index // columns
            row = self.filtered.iloc[index]

            container = QWidget()
            vbox = QVBoxLayout(container)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(0)
            vbox.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

            poster_label = QLabel()
            poster_label.setFixedSize(120, 180)
            poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            def emit_row(event, row_data=row.to_dict()):
                self.poster_clicked.emit(row_data)

            poster_label.mousePressEvent = emit_row

            poster_rel_path = Path(row["poster_path"].strip().lstrip("\\/"))
            img_path = PROJECT_ROOT / "data" / poster_rel_path
            abs_path = img_path.resolve()

            if img_path.exists():
                loader = ImageLoader(str(img_path), poster_label, self.image_signal)
                self.threadpool.start(loader)
            else:
                print(f"File not found: {abs_path}")

            title_label = QLabel(row["title"])
            title_label.setFixedSize(120, 50)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setWordWrap(True)
            title_label.setStyleSheet("background-color: transparent;")

            vbox.addWidget(poster_label)
            vbox.addWidget(title_label)

            self.grid.addWidget(container, row_pos, col, alignment=Qt.AlignmentFlag.AlignTop)

        self.loaded_items += self.batch_size
        self.container.setMinimumHeight((self.loaded_items // columns + 1) * 220)

    def set_poster_image(self, qimage, label):
        try:
            if isinstance(label, QLabel):
                pixmap = QPixmap.fromImage(qimage)
                if not pixmap.isNull():
                    label.setPixmap(pixmap)
        except RuntimeError:
            pass

    def on_scroll(self, value):
        max_value = self.scroll.verticalScrollBar().maximum()
        if value > max_value - 100:
            if self.loaded_items < len(self.filtered):
                self.populate_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reload_grid()

    def reload_grid(self):
        self.loaded_items = 0
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.populate_grid()
