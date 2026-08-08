import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl, QDir, QSize
from PySide6.QtGui import QFont, QPixmap, QFontDatabase, QDesktopServices
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (QApplication, 
                               QLabel, 
                               QMainWindow,
                               QPushButton,
                               QVBoxLayout,
                               QHBoxLayout, 
                               QWidget,
                               QSlider,
                               QStackedWidget,
                               )

from model import PomodoroTimer

ASSETS = Path(__file__).parent / "assets"

DEFAULT_WORK_MIN = 25
DEFAULT_SHORT_BREAK_MIN = 5
DEFAULT_LONG_BREAK_MIN = 15
DEFAULT_CYCLES = 4


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
    def __init__(self, minimum, maximum, default, step, on_change=None):
        super().__init__()
        self.on_change = on_change

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        sound_button=QPushButton("Vol")
        sound_button.setObjectName("soundButton")
        sound_button.setFixedSize(40, 40)
        sound_button.setCheckable(True)
        sound_button.clicked.connect(self._toggle_slider)
        self.vol_slider = QSlider(Qt.Orientation.Vertical)
        self.vol_slider.setRange(minimum, maximum)
        self.vol_slider.setValue(default)
        self.vol_slider.setSingleStep(step)
        self.vol_slider.hide()
        self.vol_slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(sound_button)
        layout.addWidget(self.vol_slider)

    def _toggle_slider(self, checked):
        if checked:
            self.vol_slider.show()
        else:
            self.vol_slider.hide()

    def _on_value_changed(self, value):
        normalized = value / 100
        if self.on_change:
            self.on_change(normalized)
     
    def value(self):
        return self.vol_slider.value() / 100


class FloatingWindow(QWidget):
    def __init__(self, on_hide):
        super().__init__()
        self.on_hide = on_hide

    def update_display(self, time_text, mode_text):
        self.time_label.setText(time_text)
        self.time_label.setText(mode_text)

    def hide(self, event):
        if self.on_hide:
            self.on_hide()
        super().hide(event)

    def mousePressEvent(self, event):
            self._old_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        self._old_pos = None


class StartMenu(QWidget):
    def __init__(self, on_settings, on_play, on_close):
        super().__init__()
        self.on_settings = on_settings
        self.on_play = on_play
        self.on_close = on_close

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 0)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(40, 40)
        close_button.clicked.connect(self.on_close)
        close_row.addWidget(close_button)
        layout.addLayout(close_row)
        layout.addStretch(1)

        title = QLabel("Fungi Pomodoro Timer")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addStretch(1)

        self.mascot = QLabel()
        self.mascot.setAlignment(Qt.AlignCenter)
        self.mascot.setFixedHeight(180)
        layout.addWidget(self.mascot)
        path = ASSETS / "fungi-time.png"
        pix = QPixmap(str(path))
        self.mascot.setPixmap(
                    pix.scaled(180, 180, Qt.KeepAspectRatio, Qt.FastTransformation)
        )
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
        

class SetupPage(QWidget):
    def __init__(self, on_start, on_menu, on_close):
        super().__init__()
        self.on_start = on_start
        self.on_menu = on_menu
        self.on_close = on_close

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 0)
        layout.setSpacing(20)

        top_row = QHBoxLayout()
        menu_button = QPushButton("Menu")
        menu_button.setObjectName("menuButton")
        menu_button.clicked.connect(self._menu_clicked)
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(40, 40)
        close_button.clicked.connect(self.on_close)
        top_row.addWidget(menu_button)
        top_row.addStretch(1)
        top_row.addWidget(close_button)
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


class TimerPage(QWidget):
    def __init__(self, model, on_back, on_menu, on_close, volume=0.5, floating_window=None):
        super().__init__()
        self.model = model
        self.on_back = on_back
        self.on_menu = on_menu
        self.on_close = on_close
        self.volume = volume

        self._build_ui()
        self._load_sound(volume=self.volume)

        self.model.state_changed.connect(self._refresh_display)
        self.model.mode_changed.connect(self.ding.play)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.model.tick)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 0)

        top_row = QHBoxLayout()
        back_button = QPushButton("Settings")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self._back_clicked)
        menu_button = QPushButton("Menu")
        menu_button.setObjectName("menuButton")
        menu_button.clicked.connect(self._menu_clicked)
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(40, 40)
        close_button.clicked.connect(self.on_close)
        top_row.addWidget(menu_button)
        top_row.addWidget(back_button)
        top_row.addStretch(1)
        top_row.addWidget(close_button)
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

    def _set_mascot_for_mode(self):
        filename = {"Work": "mascot_work.png",
                    "Short break": "mascot_short_break.png",
                    "Long break": 'mascot_long_break.png',
                    }[self.model.mode]
        path = ASSETS / filename
        if path.exists():
            pix = QPixmap(str(path))
            self.mascot.setPixmap(
                pix.scaled(140, 140, Qt.KeepAspectRatio, Qt.FastTransformation)
            )
        else:
            self.mascot.setText("🍅" if self.mode == "work" else "☕")
            self.mascot.setFont(QFont("Arial", 48))


class MainPomodoroWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mushroom Timer 🍄")
        self.setFixedSize(400, 540)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        root = QWidget()
        root.setObjectName("root")
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        
        lower_row = QHBoxLayout()
        github_button = QPushButton("")
        github_button.setObjectName("githubButton")
        github_button.clicked.connect(self._github_clicked)
        github_button.setFixedSize(40, 30)
        size = QSize(20, 20)
        path = ASSETS / "GitHub_Invertocat_Black_Clearspace.png"
        pix = QPixmap(str(path))
        github_button.setIcon(pix)
        github_button.setIconSize(size)
        linkedin_button = QPushButton("")
        linkedin_button.setObjectName("linkedinButton")
        linkedin_button.clicked.connect(self._linkedin_clicked)
        linkedin_button.setFixedSize(40, 30)
        size = QSize(20, 20)
        path = ASSETS / "linkedin.png"
        pix = QPixmap(str(path))
        linkedin_button.setIcon(pix)
        linkedin_button.setIconSize(size)
        mail_button = QPushButton("")
        mail_button.setObjectName("mailButton")
        mail_button.clicked.connect(self._sent_mail)
        mail_button.setFixedSize(50, 30)
        size = QSize(25, 25)
        path = ASSETS / "mail.png"
        pix = QPixmap(str(path))
        mail_button.setIcon(pix)
        mail_button.setIconSize(size)
        self.volume_button = VolumeSlider(
            0, 100, 50, 1, on_change=self._on_volume_changed
        )
        lower_row.addWidget(github_button)
        lower_row.addWidget(linkedin_button)
        lower_row.addWidget(mail_button)
        lower_row.addStretch()
        lower_row.addWidget(self.volume_button)
        lower_row.setContentsMargins(20, 0, 20, 20)

        self.setCentralWidget(root)

        self.model = PomodoroTimer(DEFAULT_WORK_MIN,
                                   DEFAULT_SHORT_BREAK_MIN,
                                   DEFAULT_CYCLES,
                                   DEFAULT_LONG_BREAK_MIN)

        self.stack = QStackedWidget()
        self.start_menu = StartMenu(on_play=self._start_timer, 
                                    on_settings=self._show_setup, 
                                    on_close=self.close)
        self.setup_page = SetupPage(on_start=self._start_timer, 
                                    on_menu=self._start_menu, 
                                    on_close=self.close)
        self.timer_page = TimerPage(model=self.model,
                                    on_back=self._show_setup, 
                                    on_menu=self._start_menu, 
                                    on_close=self.close)

        self.stack.addWidget(self.start_menu)
        self.stack.addWidget(self.setup_page)
        self.stack.addWidget(self.timer_page)
        outer.addWidget(self.stack)
        outer.addLayout(lower_row)

        self.setCentralWidget(root)

        self._apply_styles()

        self._old_pos = None

    def _apply_styles(self):

        QDir.addSearchPath("assets", str(ASSETS))

        font_path = ASSETS / "super-joyful-font" / "super-joyful.ttf"
        # font_path = ASSETS / "return-of-the-boss-font" / "return-of-the-boss.ttf"
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
 
        qss_path = Path(__file__).parent / "pastel_style.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text())

    def _start_timer(self, work_min, short_break_min, long_break_min, cycles):
        self.model.configure(work_min, short_break_min, long_break_min, cycles)
        self.stack.setCurrentWidget(self.timer_page)

    def _show_setup(self):
        self.stack.setCurrentWidget(self.setup_page)

    def _start_menu(self):
        self.stack.setCurrentWidget(self.start_menu)

    def _github_clicked(self):
        webbrowser.open('https://github.com/ReneeLocr')

    def _linkedin_clicked(self):
        webbrowser.open('https://linkedin.com')

    def _sent_mail(self):
        email = "renee.locreille@uclouvain.be"
        subject = "Timer app"
        url = f"mailto:{email}?subject={subject}"

        QDesktopServices.openUrl(QUrl(url))

    def _on_volume_changed(self, value):
        self.timer_page.set_volume(value)

    def mousePressEvent(self, event):
        self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._old_pos = None


def main():
    app = QApplication(sys.argv)
    window = MainPomodoroWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()