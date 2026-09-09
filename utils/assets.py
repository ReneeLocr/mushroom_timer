from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFontDatabase

from config import ASSETS, FONT_PATH, QSS_PATH

def load_stylesheet():
    """Load the application's QSS stylesheet if it exists."""
    if QSS_PATH.exists():
        return QSS_PATH.read_text(encoding="utf-8")

def load_font():
    """Load the custom application font if available."""
    if FONT_PATH.exists():
        QFontDatabase.addApplicationFont(str(FONT_PATH))


def load_pixmap(filename):
    """Load an image from the assets directory."""
    path = ASSETS / filename

    if not path.exists():
        return QPixmap()

    return QPixmap(str(path))


def scale_pixmap(pixmap, width, height):
    """Scale a pixmap while preserving its aspect ratio."""
    if pixmap.isNull():
        return pixmap
    return pixmap.scaled(
        width,
        height,
        Qt.KeepAspectRatio,
    )