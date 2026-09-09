import sys
import os

from PySide6.QtWidgets import QApplication # type: ignore
from PySide6.QtGui import QIcon

from ui.window import MainPomodoroWindow
from config import APP_ICON, BASE_DIR

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(BASE_DIR, APP_ICON)))
    window = MainPomodoroWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()