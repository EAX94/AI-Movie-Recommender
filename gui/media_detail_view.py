from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy, QGridLayout, QScrollArea
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal
from pathlib import Path
import pandas as pd
from src.config import METADATA_PATH
from src.recommender import get_recommendations, get_cached_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]

class MediaDetailView(QWidget):
    back_clicked = Signal()
    similar_clicked = Signal(dict)

    def __init__(self, metadata: dict, parent=None):
        super().__init__(parent)
        self.metadata = metadata

        main_layout = QVBoxLayout(self)

        # Back button
        back_layout = QHBoxLayout()
        back_button = QPushButton()
        icon_path = Path(__file__).parent / "assets" / "back_arrow.png"
        if icon_path.exists():
            back_button.setIcon(QIcon(str(icon_path)))
        else:
            back_button.setText("\u2190 Back")
        back_button.setFixedSize(80, 30)
        back_button.clicked.connect(self.back_clicked.emit)
        back_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(back_layout)

        layout = QHBoxLayout()

        # Poster image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        if "poster_path" in metadata:
            poster_path = Path(metadata["poster_path"].strip().lstrip("/\\"))
            img_path = PROJECT_ROOT / "data" / poster_path
            if img_path.exists():
                pixmap = QPixmap(str(img_path))
                if not pixmap.isNull():
                    image_label.setPixmap(pixmap.scaled(240, 360, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(image_label)

        info_layout = QVBoxLayout()

        # Metadata fields
        for key in ["title", "name", "release_date", "first_air_date", "genres", "overview"]:
            if key in metadata:
                label = QLabel(f"<b>{key.replace('_', ' ').title()}:</b> {metadata[key]}")
                label.setWordWrap(True)
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                info_layout.addWidget(label)

        info_layout.addStretch()
        layout.addLayout(info_layout)
        main_layout.addLayout(layout)

        # Similar items section
        similar_label = QLabel("<b>Similar:</b>")
        main_layout.addWidget(similar_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        grid = QGridLayout(scroll_widget)

        df = get_cached_dataset()
        titles = get_recommendations(df, metadata.get("title", ""), top_n=10)
        similar_items = df[df["title"].isin(titles)].to_dict(orient="records")

        for idx, item in enumerate(similar_items):
            col = idx % 5
            row = idx // 5

            item_container = QWidget()
            vbox = QVBoxLayout(item_container)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(5)

            poster_label = QLabel()
            poster_label.setFixedSize(120, 180)
            poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            poster_label.mousePressEvent = self.create_click_handler(item)
            poster_path = Path(item["poster_path"].strip().lstrip("/\\"))
            img_path = PROJECT_ROOT / "data" / poster_path
            if img_path.exists():
                pixmap = QPixmap(str(img_path))
                if not pixmap.isNull():
                    poster_label.setPixmap(pixmap.scaled(120, 180, Qt.AspectRatioMode.KeepAspectRatio))

            title_label = QLabel(item.get("title", "Untitled"))
            title_label.setFixedSize(120, 40)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setWordWrap(True)
            vbox.addWidget(poster_label)
            vbox.addWidget(title_label)

            grid.addWidget(item_container, row, col)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def create_click_handler(self, item):
        def handler(event):
            self.similar_clicked.emit(item)
        return handler
