from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, 
                               QPushButton,
                               QVBoxLayout,
                               QWidget,
                               )

from utils.assets import load_pixmap, scale_pixmap
from config import (DEFAULT_WORK_MIN, 
                    DEFAULT_SHORT_BREAK_MIN, 
                    DEFAULT_LONG_BREAK_MIN, 
                    DEFAULT_CYCLES,
                    MASCOT_SIZE_MENU,
                    )


class StartMenu(QWidget):
    def __init__(self, on_settings, on_play, on_close):
        super().__init__()
        self.on_settings = on_settings
        self.on_play = on_play
        self.on_close = on_close

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 0)
        layout.addStretch(2)

        title = QLabel("Fungi Pomodoro Timer")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addStretch(1)

        self.mascot = QLabel()
        self.mascot.setAlignment(Qt.AlignCenter)
        self.mascot.setFixedHeight(MASCOT_SIZE_MENU)
        layout.addWidget(self.mascot)
        pix = load_pixmap("fungi-time.png")
        self.mascot.setPixmap(scale_pixmap(pix, MASCOT_SIZE_MENU, MASCOT_SIZE_MENU))
        layout.addStretch(1)

        button_row = QVBoxLayout()
        button_row.setContentsMargins(10, 10, 10, 10)
        play_button = QPushButton("Play")
        play_button.setObjectName("playButton")
        play_button.clicked.connect(self._play_clicked)
        set_button = QPushButton("Settings")
        set_button.setObjectName("settingsButton")
        set_button.clicked.connect(self._settings_clicked)
        button_row.addWidget(play_button)
        button_row.addWidget(set_button)
        layout.addLayout(button_row)

    def _settings_clicked(self):
        self.on_settings()

    def _play_clicked(self):
        self.on_play(work_min = DEFAULT_WORK_MIN,
                     short_break_min = DEFAULT_SHORT_BREAK_MIN,
                     long_break_min = DEFAULT_LONG_BREAK_MIN,
                     cycles = DEFAULT_CYCLES)