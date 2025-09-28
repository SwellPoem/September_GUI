import tkinter as tk
import config
from PIL import Image, ImageTk

def setup_graphics(window):
    canvas = tk.Canvas(window, width=config.CANVAS_WIDTH, height=config.CANVAS_HEIGHT,
                       bg=config.BG_COLOR, highlightthickness=0)
    canvas.pack()

    # --- Café background ---
    try:
        cafe_img_raw = Image.open(config.CAFE_BG_PATH).resize((config.CANVAS_WIDTH, config.CANVAS_HEIGHT))
        cafe_bg = ImageTk.PhotoImage(cafe_img_raw)
        canvas.create_image(0, 0, anchor="nw", image=cafe_bg)
        canvas.cafe_bg = cafe_bg
    except Exception as e:
        print("Background image not found:", e)

    # --- Semi-transparent backgrounds for title and timer ---
    # Pillow RGBA: (R,G,B,Alpha), Alpha=160 is semi-transparent, 255 is opaque
    rect_title_img = Image.new("RGBA", (300, 60), (247, 234, 217, 160))
    rect_title_tk = ImageTk.PhotoImage(rect_title_img)
    canvas.create_image(config.CANVAS_WIDTH//2 - 150, 40, anchor="nw", image=rect_title_tk)
    canvas.rect_title_tk = rect_title_tk

    rect_timer_img = Image.new("RGBA", (300, 60), (247, 234, 217, 160))
    rect_timer_tk = ImageTk.PhotoImage(rect_timer_img)
    canvas.create_image(config.CANVAS_WIDTH//2 - 150, 120, anchor="nw", image=rect_timer_tk)
    canvas.rect_timer_tk = rect_timer_tk

    # --- Title label and timer text ---
    title_label_canvas = canvas.create_text(
        config.CANVAS_WIDTH // 2, 70,
        text="Timer", fill=config.TITLE_TEXT_COLOR, font=config.FONT
    )
    timer_overlay = canvas.create_text(
        config.CANVAS_WIDTH // 2, 150,
        text="00:00", fill=config.TIMER_TEXT_COLOR, font=config.TIMER_FONT
    )

    # --- Controls ---
    work_minutes = tk.IntVar(value=config.DEFAULT_WORK_MIN)
    work_seconds = tk.IntVar(value=config.DEFAULT_WORK_SEC)
    break_minutes = tk.IntVar(value=config.DEFAULT_BREAK_MIN)
    break_seconds = tk.IntVar(value=config.DEFAULT_BREAK_SEC)

    checkmarks_label = tk.Label(window, fg="#b9a394", bg=config.BG_COLOR, font=config.FONT)
    canvas.create_window(config.CANVAS_WIDTH // 2, 210, window=checkmarks_label)

    spn_y = 250
    canvas.create_text(320, spn_y, text="Work Min", font=config.FONT, fill=config.TIMER_TEXT_COLOR)
    spin_work_min = tk.Spinbox(window, from_=0, to=59, textvariable=work_minutes, width=2, font=config.FONT)
    canvas.create_window(400, spn_y, window=spin_work_min)
    canvas.create_text(460, spn_y, text="Sec", font=config.FONT, fill=config.TIMER_TEXT_COLOR)
    spin_work_sec = tk.Spinbox(window, from_=0, to=59, textvariable=work_seconds, width=2, font=config.FONT)
    canvas.create_window(520, spn_y, window=spin_work_sec)
    canvas.create_text(680, spn_y, text="Break Min", font=config.FONT, fill=config.TIMER_TEXT_COLOR)
    spin_break_min = tk.Spinbox(window, from_=0, to=59, textvariable=break_minutes, width=2, font=config.FONT)
    canvas.create_window(760, spn_y, window=spin_break_min)
    canvas.create_text(820, spn_y, text="Sec", font=config.FONT, fill=config.TIMER_TEXT_COLOR)
    spin_break_sec = tk.Spinbox(window, from_=0, to=59, textvariable=break_seconds, width=2, font=config.FONT)
    canvas.create_window(880, spn_y, window=spin_break_sec)

    return {
        'canvas': canvas,
        'timer_overlay': timer_overlay,
        'title_label_canvas': title_label_canvas,
        'work_minutes': work_minutes,
        'work_seconds': work_seconds,
        'break_minutes': break_minutes,
        'break_seconds': break_seconds,
        'checkmarks_label': checkmarks_label,
        'spin_work_min': spin_work_min,
        'spin_work_sec': spin_work_sec,
        'spin_break_min': spin_break_min,
        'spin_break_sec': spin_break_sec,
    }