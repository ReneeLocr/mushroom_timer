from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, 
                               QPushButton,
                               QVBoxLayout,
                               QHBoxLayout, 
                               QWidget,
                               )

from config import *
from utils import LabeledSlider


class SetupPage(QWidget):
    def __init__(self, on_start, on_menu, on_close):
        super().__init__()
        self.on_start = on_start
        self.on_menu = on_menu
        self.on_close = on_close

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 0)

        top_row = QHBoxLayout()
        menu_button = QPushButton("Menu")
        menu_button.setObjectName("menuButton")
        menu_button.clicked.connect(self._menu_clicked)
        menu_button.setFixedHeight(40)
        top_row.addWidget(menu_button)
        top_row.addStretch()
        layout.addLayout(top_row)
        layout.addStretch()

        title = QLabel("Timer Settings")
        title.setObjectName("setupTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addStretch()

        self.work_slider = LabeledSlider(
            "Working time", 5, 100, DEFAULT_WORK_MIN, step=5, suffix=" min"
            )

        self.short_break_slider = LabeledSlider(
            "Short break", 1, 15, DEFAULT_SHORT_BREAK_MIN, step=1, suffix=" min"
            )

        self.long_break_slider = LabeledSlider(
            "Long break", 5, 30, DEFAULT_LONG_BREAK_MIN, step=5, suffix=" min"
            )

        self.cycles_slider = LabeledSlider(
            "Cycles before long break", 1, 8, DEFAULT_CYCLES, step=1
            )

        sliders = QVBoxLayout()
        for slider in (self.work_slider,
                       self.short_break_slider,
                       self.long_break_slider,
                       self.cycles_slider):
            sliders.addWidget(slider)
        sliders.setContentsMargins(10, 10, 10, 10)
        layout.addLayout(sliders)

        layout.addStretch()

        button_row = QHBoxLayout()
        start_button = QPushButton("Start")
        start_button.setObjectName("startButton")
        start_button.clicked.connect(self._start_clicked)
        button_row.addWidget(start_button)
        button_row.setContentsMargins(10, 10, 10, 10)
        layout.addLayout(button_row)

    def _menu_clicked(self):
        self.on_menu()

    def _start_clicked(self):
        self.on_start(work_min=self.work_slider.value(),
                      short_break_min=self.short_break_slider.value(),
                      long_break_min=self.long_break_slider.value(),
                      cycles=self.cycles_slider.value())