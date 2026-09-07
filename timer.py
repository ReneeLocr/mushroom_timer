from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (QLabel, 
                               QPushButton,
                               QVBoxLayout,
                               QHBoxLayout, 
                               QWidget,
                               )

from config import ASSETS, Mode, WORK_MASCOT, SHORT_BREAK_MASCOT, LONG_BREAK_MASCOT
from utils import load_pixmap, scale_pixmap


class TimerPage(QWidget):
    def __init__(self, model, timer, on_back, on_menu, on_close, volume=0.5, floating_window=None):
        super().__init__()
        self.model = model
        self.timer = timer
        self.on_back = on_back
        self.on_menu = on_menu
        self.on_close = on_close
        self.volume = volume
        self.floating_window = floating_window

        self._build_ui()
        self._load_sound(volume=self.volume)

        self.model.state_changed.connect(self._refresh_display)
        self.model.mode_changed.connect(self.ding.play)

        self._refresh_display()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 0)

        top_row = QHBoxLayout()
        back_button = QPushButton("Settings")
        back_button.setObjectName("backButton")
        back_button.setFixedHeight(40)
        back_button.clicked.connect(self._back_clicked)
        menu_button = QPushButton("Menu")
        menu_button.setObjectName("menuButton")
        menu_button.setFixedHeight(40)
        menu_button.clicked.connect(self._menu_clicked)
        self.pin_button = QPushButton("📌")
        self.pin_button.setObjectName("pinButton")
        self.pin_button.setFixedSize(40, 40)
        self.pin_button.setCheckable(True)
        self.pin_button.clicked.connect(self._toggle_floating)
        top_row.addWidget(menu_button)
        top_row.addWidget(back_button)
        top_row.addWidget(self.pin_button)
        top_row.addStretch(1)
        layout.addLayout(top_row)
        layout.addStretch()

        self.mascot = QLabel()
        self.mascot.setAlignment(Qt.AlignCenter)
        self.mascot.setFixedHeight(140)
        layout.addWidget(self.mascot)
        layout.addStretch()

        self.mode_label = QLabel("Working time")
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mode_label)
        layout.addStretch()

        self.time_label = QLabel("25:00")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
 
        self.cycle_label = QLabel("○ ○ ○ ○")
        self.cycle_label.setObjectName("cycleLabel")
        self.cycle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.cycle_label)
        layout.addStretch() 

        button_row = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.toggle_running)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.reset_button)
        button_row.setContentsMargins(10, 10, 10, 10)
        layout.addLayout(button_row)

    def _load_sound(self, volume):
        self.ding = QSoundEffect()
        sound_path = ASSETS / "ding.wav"
        if sound_path.exists(): 
            self.ding.setSource(QUrl.fromLocalFile(str(sound_path)))
            self.ding.setVolume(volume)

    def set_volume(self, volume):
        self.volume = volume
        self.ding.setVolume(volume)

    def _back_clicked(self):
        self.model.pause()
        self.timer.stop()
        self.start_button.setText("Start")
        self.on_back()

    def _menu_clicked(self):
        self.model.pause()
        self.timer.stop()
        self.start_button.setText("Start")
        self.on_menu()

    def _toggle_floating(self, checked):
        if not self.floating_window:
            return
        if checked:
            self.floating_window.show()
        else:
            self.floating_window.hide()

    def toggle_running(self):
        if self.model.running:
            self.model.pause()
            self.timer.stop()
        else:
            self.model.start()
            self.timer.start()
        
        self.start_button.setText("Pause" if self.model.running else "Start")

    def reset_timer(self):
        self.timer.stop()
        self.model.reset_timer()
        self.start_button.setText("Start")

    def _refresh_display(self):
        self.time_label.setText(self.model.formatted_time())
        self.mode_label.setText(self.model.mode_label())
        self.cycle_label.setText(self.model.cycle_dots())
        self._set_mascot_for_mode()
        self.start_button.setText("Pause" if self.model.running else "Start")

    def _set_mascot_for_mode(self):
        filename = {Mode.WORK.value: WORK_MASCOT,
                    Mode.SHORT_BREAK.value: SHORT_BREAK_MASCOT,
                    Mode.LONG_BREAK.value: LONG_BREAK_MASCOT,
                    }[self.model.mode]
        pix = load_pixmap(filename)
        self.mascot.setPixmap(scale_pixmap(pix, 140, 140))