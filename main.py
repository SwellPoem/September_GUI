import tkinter as tk
import config
from graphics import setup_graphics
from pomodoro import PomodoroTimer
from animation import LeafAnimator

# Orange Button style dictionary
button_style = {
    "font": ("Segoe UI", 16, "bold"),
    "bg": "#ff9800",                # Orange background
    "fg": "#4e3b2c",                # Text color
    "activebackground": "#ffa726",  # Lighter orange when active
    "activeforeground": "#fffbe6",  # Light text when active
    "highlightbackground": "#ff9800", # For macOS
    "highlightcolor": "#ff9800",      # For macOS
    "disabledforeground": "#fffbe6",  # Disabled text color
    "relief": "flat",
    "borderwidth": 0,
    "padx": 20,
    "pady": 12,
}

def force_orange(btn):
    btn.configure(bg="#ff9800", highlightbackground="#ff9800", highlightcolor="#ff9800")

def main():
    window = tk.Tk()
    window.title(config.APP_TITLE)
    window.config(bg=config.BG_COLOR)

    ui = setup_graphics(window)
    canvas = ui['canvas']
    canvas.config(highlightthickness=0)

    animator = LeafAnimator(window, canvas)

    pomodoro = PomodoroTimer(
        window, canvas,
        ui['timer_overlay'],
        ui['title_label_canvas'],
        ui['checkmarks_label'],
        ui['work_minutes'], ui['work_seconds'],
        ui['break_minutes'], ui['break_seconds']
    )

    btn_y = 300
    btn_xs = [250, 500, 750, 1000]
    start_button = tk.Button(window, text="Start", command=pomodoro.start_timer, **button_style)
    canvas.create_window(btn_xs[0], btn_y, window=start_button)
    reset_button = tk.Button(window, text="Reset", command=pomodoro.reset_timer, **button_style)
    canvas.create_window(btn_xs[1], btn_y, window=reset_button)
    pause_button = tk.Button(window, text="Pause", command=pomodoro.pause_timer, **button_style)
    canvas.create_window(btn_xs[2], btn_y, window=pause_button)
    resume_button = tk.Button(window, text="Resume", command=pomodoro.resume_timer, **button_style)
    canvas.create_window(btn_xs[3], btn_y, window=resume_button)

    skip_y = 370
    skip_xs = [400, 800]
    skip_button_style = button_style.copy()
    skip_button_style.update({"width": 16})
    skip_to_break_button = tk.Button(window, text="Skip to Break", command=pomodoro.skip_to_break, **skip_button_style)
    canvas.create_window(skip_xs[0], skip_y, window=skip_to_break_button)

    skip_to_work_button = tk.Button(window, text="Skip to Work", command=pomodoro.skip_to_work, **skip_button_style)
    canvas.create_window(skip_xs[1], skip_y, window=skip_to_work_button)

    # --- Bind focus events to keep buttons orange ---
    btns = [start_button, reset_button, pause_button, resume_button, skip_to_break_button, skip_to_work_button]
    for b in btns:
        b.bind("<FocusIn>", lambda e, b=b: force_orange(b))
        b.bind("<FocusOut>", lambda e, b=b: force_orange(b))

    window.mainloop()

if __name__ == "__main__":
    main()