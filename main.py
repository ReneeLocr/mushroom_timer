import sys

from PySide6.QtWidgets import QApplication # type: ignore

from window import MainPomodoroWindow

def main():
    app = QApplication(sys.argv)
    window = MainPomodoroWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()