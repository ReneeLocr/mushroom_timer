import webbrowser

from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QMainWindow,
                               QPushButton,
                               QVBoxLayout,
                               QHBoxLayout, 
                               QWidget,
                               QStackedWidget,
                               )

from model import PomodoroTimer
from utils import *
from config import *
from menu import StartMenu
from setup import SetupPage
from timer import TimerPage


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
        github_button.setFixedSize(40, 40)
        size = QSize(25, 25)
        pix = load_pixmap(GITHUB_ICON)
        github_button.setIcon(pix)
        github_button.setIconSize(size)
        linkedin_button = QPushButton("")
        linkedin_button.setObjectName("linkedinButton")
        linkedin_button.clicked.connect(self._linkedin_clicked)
        linkedin_button.setFixedSize(40, 40)
        size = QSize(25, 25)
        pix = load_pixmap(IN_ICON)
        linkedin_button.setIcon(pix)
        linkedin_button.setIconSize(size)
        mail_button = QPushButton("")
        mail_button.setObjectName("mailButton")
        mail_button.clicked.connect(self._sent_mail)
        mail_button.setFixedSize(50, 40)
        size = QSize(30, 30)
        pix = load_pixmap(MAIL_ICON)
        mail_button.setIcon(pix)
        mail_button.setIconSize(size)
        self.volume_button = QPushButton("")
        self.volume_button.setObjectName("volButton")
        self.volume_button.setFixedSize(40, 40)
        self.volume_button.setCheckable(True)
        self.volume_button.clicked.connect(self._toggle_volume)
        size = QSize(30, 30)
        pix = load_pixmap(VOLUME_ICON)
        self.volume_button.setIcon(pix)
        self.volume_button.setIconSize(size)
        lower_row.addWidget(github_button)
        lower_row.addWidget(linkedin_button)
        lower_row.addWidget(mail_button)
        lower_row.addStretch()
        lower_row.addWidget(self.volume_button)
        lower_row.setContentsMargins(20, 0, 20, 20)

        self.model = PomodoroTimer(DEFAULT_WORK_MIN,
                                   DEFAULT_SHORT_BREAK_MIN,
                                   DEFAULT_LONG_BREAK_MIN,
                                   DEFAULT_CYCLES)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.model.tick)

        self.floating_window = FloatingWindow(
            model=self.model, timer=self.timer, 
            on_hide=self._on_floating_hidden
        )
        self.volume_slider = VolumeSlider(
            0, 100, 50, 1, 
            on_change=self._on_volume_changed,
            on_hide=self._on_volume_hidden
        )

        self.stack = QStackedWidget()
        self.start_menu = StartMenu(on_play=self._start_timer, 
                                    on_settings=self._show_setup, 
                                    on_close=self.close)
        self.setup_page = SetupPage(on_start=self._start_timer, 
                                    on_menu=self._start_menu, 
                                    on_close=self.close)
        self.timer_page = TimerPage(model=self.model,
                                    timer=self.timer,
                                    on_back=self._show_setup, 
                                    on_menu=self._start_menu, 
                                    on_close=self.close,
                                    floating_window=self.floating_window)

        self.stack.addWidget(self.start_menu)
        self.stack.addWidget(self.setup_page)
        self.stack.addWidget(self.timer_page)
        outer.addWidget(self.stack)
        outer.addLayout(lower_row)

        self.close_button = QPushButton("×", root) 
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(40, 40)
        self.close_button.clicked.connect(self.close)
        self.close_button.move(340, 20)  
        self.close_button.raise_()

        self.minimize_button = QPushButton("-", root) 
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(40, 40)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.minimize_button.move(292, 20)  
        self.minimize_button.raise_()

        self.setCentralWidget(root)

        self._apply_styles()

        self._old_pos = None

    def _apply_styles(self):
        load_font()
        stylesheet = load_stylesheet()
        self.setStyleSheet(stylesheet)


    def _start_timer(self, work_min, short_break_min, long_break_min, cycles):
        self.model.configure(work_min, short_break_min, long_break_min, cycles)
        self.timer.stop()
        self.stack.setCurrentWidget(self.timer_page)
        self.timer_page._refresh_display()

    def _show_setup(self):
        self.timer.stop()
        self.model.pause()
        self.stack.setCurrentWidget(self.setup_page)

    def _start_menu(self):
        self.timer.stop()
        self.model.pause()
        self.stack.setCurrentWidget(self.start_menu)

    def _github_clicked(self):
        webbrowser.open(GITHUB_URL)

    def _linkedin_clicked(self):
        webbrowser.open(LINKEDIN_URL)

    def _sent_mail(self):
        email = EMAIL_ADDRESS
        subject = EMAIL_SUBJECT
        url = f"mailto:{email}?subject={subject}"

        QDesktopServices.openUrl(QUrl(url))

    def _on_volume_changed(self, value):
        self.timer_page.set_volume(value)

    def _on_floating_hidden(self):
        self.timer_page.pin_button.setChecked(False)

    def _on_volume_hidden(self):
        self.volume_button.setChecked(False)

    def _toggle_volume(self, checked):
        if checked:
            button = self.volume_button
            glob_pos = button.mapToGlobal(button.rect().topLeft())
            self.volume_slider.move(
                glob_pos.x() ,
                glob_pos.y() - self.volume_slider.height() - 5
            )
            self.volume_slider.show()
        else:
            self.volume_slider.hide()

    def mousePressEvent(self, event):
        self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()

            if self.volume_slider.isVisible():
                self.volume_slider.move(
                    self.volume_slider.x() + delta.x(),
                    self.volume_slider.y() + delta.y()
                )
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._old_pos = None

    def closeEvent(self, event):
        self.floating_window.close()
        super().closeEvent(event)


