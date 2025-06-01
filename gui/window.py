from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from gui.poster_widget import PosterWidget
from gui.media_grid_view import MediaGridView
from gui.media_detail_view import MediaDetailView

class MovieRecommenderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Movie Recommender")
        self.resize(1280, 720)

        screen = self.screen().availableGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

        self.movies_view = MediaGridView("movie", parent=self)
        self.tv_view = MediaGridView("tv", parent=self)
        self.detail_view = None
        self.current_grid = None

        self.show_home()

    def show_home(self):
        central = QWidget()
        layout = QHBoxLayout(central)

        movie_poster = PosterWidget("movies.jpeg", "Movies")
        tv_poster = PosterWidget("tv.jpg", "TV Shows")

        movie_poster.clicked.connect(lambda: self.show_grid("movie"))
        tv_poster.clicked.connect(lambda: self.show_grid("tv"))

        h_layout = QHBoxLayout()
        h_layout.addStretch()

        poster_container_1 = QWidget()
        poster_layout_1 = QVBoxLayout()
        poster_layout_1.addWidget(movie_poster)
        poster_container_1.setLayout(poster_layout_1)

        poster_container_2 = QWidget()
        poster_layout_2 = QVBoxLayout()
        poster_layout_2.addWidget(tv_poster)
        poster_container_2.setLayout(poster_layout_2)

        h_layout.addWidget(poster_container_1)
        h_layout.addSpacing(50)
        h_layout.addWidget(poster_container_2)
        h_layout.addStretch()

        layout.addLayout(h_layout)
        self.setCentralWidget(central)

    def show_grid(self, media_type):
        if media_type == "movie":
            self.current_grid = self.movies_view
        else:
            self.current_grid = self.tv_view

        self.current_grid.back_clicked.connect(self.show_home)
        self.current_grid.poster_clicked.connect(self.show_detail_view)
        self.setCentralWidget(self.current_grid)

    def show_detail_view(self, metadata):
        self.detail_view = MediaDetailView(metadata, parent=self)
        self.detail_view.back_clicked.connect(lambda: self.setCentralWidget(self.current_grid))
        self.detail_view.similar_clicked.connect(self.show_detail_view)
        self.setCentralWidget(self.detail_view)
