import sys
from PySide6.QtWidgets import QApplication
from gui.window import MovieRecommenderGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieRecommenderGUI()
    window.show()
    sys.exit(app.exec())
