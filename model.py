from PySide6.QtCore import QObject, Signal # type: ignore


class PomodoroTimer(QObject):

    state_changed = Signal()
    mode_changed = Signal()

    def __init__(self, work_min, short_break_min, long_break_min, cycles_before_long_break):
        super().__init__()
        self.work_min = work_min
        self.short_break_min = short_break_min
        self.long_break_min = long_break_min
        self.cycles_before_long_break = cycles_before_long_break

        self.mode = "Work"
        self.cycles_completed = 0
        self.seconds_left = self.work_min * 60
        self.running = False

    def formatted_time(self) -> str:
        mins, secs = divmod(max(self.seconds_left, 0), 60)
        return f"{mins:02d}:{secs:02d}"
    
    def mode_label(self) -> str:
        labels = {
            "Work": "Working Time",
            "Short break": "Short Break",
            "Long break": "Long Break",
        }
        return labels[self.mode]

    def cycle_dots(self) -> str:
        done_in_set = self.cycles_completed % self.cycles_before_long_break
        dots = "".join(
            "●" if i < done_in_set else "○"
            for i in range(self.cycles_before_long_break)
        )
        return " ".join(dots)

    def start(self):
        self.running = True
        self.state_changed.emit()

    def pause(self):
        self.running = False
        self.state_changed.emit()

    def tick(self):
        self.seconds_left -= 1
        if self.seconds_left <= 0:
            self._advance_mode()
        self.state_changed.emit()

    def reset_timer(self):
        self.running = False
        self.mode = "Work"
        self.cycles_completed = 0
        self.seconds_left = self._duration_for_mode(self.mode) * 60
        self.state_changed.emit()

    def configure(self, work_min, short_break_min, long_break_min, cycles):
        self.work_min = work_min
        self.short_break_min = short_break_min
        self.long_break_min = long_break_min
        self.cycles_before_long_break = cycles
        self.reset_timer()

    def _advance_mode(self):
        if self.mode == "Work":
            self.cycles_completed += 1
            if self.cycles_completed % self.cycles_before_long_break == 0:
                self.mode = "Long break"
            else:
                self.mode = "Short break"
        else: 
            self.mode = "Work"
        self.seconds_left = self._duration_for_mode(self.mode) * 60
        self.mode_changed.emit()

    def _duration_for_mode(self, mode):
        return {"Work": self.work_min,
                "Short break": self.short_break_min,
                "Long break": self.long_break_min,
                }[mode]