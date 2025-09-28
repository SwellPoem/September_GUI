import math

class PomodoroTimer:
    def __init__(self, window, canvas, timer_overlay, title_label_canvas, checkmarks_label,
                 work_minutes, work_seconds, break_minutes, break_seconds):
        self.window = window
        self.canvas = canvas
        self.timer_overlay = timer_overlay
        self.title_label_canvas = title_label_canvas
        self.checkmarks_label = checkmarks_label
        self.work_minutes = work_minutes
        self.work_seconds = work_seconds
        self.break_minutes = break_minutes
        self.break_seconds = break_seconds

        self.reps = 0
        self.timer = None
        self.paused = False
        self.time_left = None

    def reset_timer(self):
        if self.timer:
            self.window.after_cancel(self.timer)
        self.canvas.itemconfig(self.timer_overlay, text="00:00")
        self.canvas.itemconfig(self.title_label_canvas, text="Timer", fill="#4e3b2c")
        self.checkmarks_label.config(text="")
        self.reps = 0
        self.paused = False
        self.time_left = None

    def start_timer(self):
        if self.timer:
            self.window.after_cancel(self.timer)
        self.paused = False
        self.time_left = None
        self.reps += 1
        if self.reps % 2 == 0:  # Break
            count = self.break_minutes.get() * 60 + self.break_seconds.get()
            self.canvas.itemconfig(self.title_label_canvas, text="Break", fill="#aec6cf")
        else:  # Work
            count = self.work_minutes.get() * 60 + self.work_seconds.get()
            self.canvas.itemconfig(self.title_label_canvas, text="Work", fill="#ffb347")
        self.count_down(count)

    def count_down(self, count):
        minutes = math.floor(count / 60)
        seconds = count % 60
        self.canvas.itemconfig(self.timer_overlay, text=f"{minutes:02d}:{seconds:02d}")
        if self.paused:
            self.time_left = count
            return
        if count > 0:
            self.timer = self.window.after(1000, self.count_down, count - 1)
        else:
            marks = "✔" * (self.reps // 2)
            self.checkmarks_label.config(text=marks)
            self.start_timer()

    def pause_timer(self):
        if self.timer:
            self.window.after_cancel(self.timer)
            current_time = self.canvas.itemcget(self.timer_overlay, "text")
            minutes, seconds = map(int, current_time.split(":"))
            self.time_left = minutes * 60 + seconds
            self.paused = True

    def resume_timer(self):
        if self.paused and self.time_left is not None and self.time_left > 0:
            self.paused = False
            self.count_down(self.time_left)
            self.time_left = None

    def skip_to_break(self):
        if self.timer:
            self.window.after_cancel(self.timer)
        self.paused = False
        self.time_left = None
        self.reps = self.reps + 1 if self.reps % 2 != 0 else self.reps
        self.canvas.itemconfig(self.title_label_canvas, text="Break", fill="#aec6cf")
        count = self.break_minutes.get() * 60 + self.break_seconds.get()
        self.count_down(count)

    def skip_to_work(self):
        if self.timer:
            self.window.after_cancel(self.timer)
        self.paused = False
        self.time_left = None
        self.reps = self.reps + 1 if self.reps % 2 == 0 else self.reps
        self.canvas.itemconfig(self.title_label_canvas, text="Work", fill="#ffb347")
        count = self.work_minutes.get() * 60 + self.work_seconds.get()
        self.count_down(count)