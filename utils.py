from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFontDatabase
from PySide6.QtWidgets import (QLabel, 
                               QPushButton,
                               QVBoxLayout,
                               QHBoxLayout, 
                               QWidget,
                               QSlider,
                               )

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


class LabeledSlider(QWidget):
    def __init__(self, title, minimum, maximum, default, step=1, suffix=""):
        super().__init__()
        self.suffix = suffix
 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
 
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("sliderTitle")
        self.value_label = QLabel(f"{default}{suffix}")
        self.value_label.setObjectName("sliderValue")
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(self.value_label)
        layout.addLayout(header)
 
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setSingleStep(step)
        self.slider.setPageStep(step)
        self.slider.setValue(default)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
 
    def _on_value_changed(self, value):
        self.value_label.setText(f"{value}{self.suffix}")
 
    def value(self):
        return self.slider.value()


class VolumeSlider(QWidget):
    def __init__(self, minimum, maximum, default, step, on_change=None, on_hide=None):
        super().__init__()
        self.on_change = on_change
        self.on_hide = on_hide

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(40, 120)

        container = QWidget(self)
        container.setObjectName("volumeContainer")
        container.setGeometry(0, 0, self.width(), self.height())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.vol_slider = QSlider(Qt.Orientation.Vertical)
        self.vol_slider.setRange(minimum, maximum)
        self.vol_slider.setValue(default)
        self.vol_slider.setSingleStep(step)
        self.vol_slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.vol_slider, alignment=Qt.AlignCenter)

        self._apply_styles()

    def _apply_styles(self):
        load_font()
        stylesheet = load_stylesheet()
        self.setStyleSheet(stylesheet)

    def _on_value_changed(self, value):
        normalized = value / 100
        if self.on_change:
            self.on_change(normalized)
     
    def value(self):
        return self.vol_slider.value() / 100

    def hideEvent(self, event):
        if self.on_hide:
            self.on_hide()
        super().hideEvent(event)


class FloatingWindow(QWidget):
    def __init__(self, model, timer, on_hide=None):
        super().__init__()
        self.model = model
        self.timer = timer
        self.on_hide = on_hide
        self._old_pos = None

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(180, 111)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget(self)
        container.setObjectName("floatingContainer")
        container_layout = QVBoxLayout(container)

        top_row = QHBoxLayout()
        top_row.addStretch()
        close_button = QPushButton("×")
        close_button.setObjectName("floatingCloseBtn")
        close_button.setFixedSize(22, 22)
        close_button.clicked.connect(self.hide)
        top_row.addWidget(close_button)
        container_layout.addLayout(top_row)

        self.mode_label = QLabel()
        self.mode_label.setObjectName("floatingModeLabel")
        self.mode_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.mode_label)

        self.time_label = QLabel()
        self.time_label.setObjectName("floatingTimeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.time_label)

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("floatingStart")
        self.start_button.clicked.connect(self.toggle_running)
        container_layout.addWidget(self.start_button)

        outer.addWidget(container)

        self.model.state_changed.connect(self._refresh)
        self._refresh()
        self._apply_styles()

    def _apply_styles(self):
        load_font()
        stylesheet = load_stylesheet()
        self.setStyleSheet(stylesheet)

    def _refresh(self):
        self.time_label.setText(self.model.formatted_time())
        self.mode_label.setText(self.model.mode_label())
        self.start_button.setText(
            "Pause" if self.model.running else "Start"
        )

    def toggle_running(self):
        if self.model.running:
            self.model.pause()
            self.timer.stop()
        else:
            self.model.start()
            self.timer.start()
        self.start_button.setText("Pause" if self.model.running else "Start")

    def hideEvent(self, event):
        if self.on_hide:
            self.on_hide()
        super().hideEvent(event)

    def mousePressEvent(self, event):
            self._old_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        self._old_pos = None