from tkinter import Canvas
from typing import Callable, Optional

from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BACKGROUND_GRADIENT_TOP, BACKGROUND_GRADIENT_BOTTOM, BACKGROUND_STEPS,
)

class MenuView:
    """
    Pixel-art styled start menu with a warm fall gradient, title, and a 'PLAY' button.
    Calls on_play when the button is clicked.
    """

    def __init__(self, master, on_play: Callable[[], None]):
        self.master = master
        self.on_play = on_play

        self.canvas = Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=False)

        self._draw_background()
        self._draw_title()
        self._draw_pixel_leaf_art(x=WINDOW_WIDTH - 140, y=60, scale=6)
        self._play_btn_bbox = self._draw_play_button()

        # Mouse bindings for button
        self.canvas.bind("<Button-1>", self._on_click)

    def destroy(self):
        self.canvas.destroy()

    # ----------------------------
    # Drawing helpers
    # ----------------------------

    def _draw_background(self):
        """
        Draw vertical gradient (same theme as game).
        Darkening is already applied in constants via chosen colors.
        """
        def hex_to_rgb(h: str):
            h = h.lstrip("#")
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

        def rgb_to_hex(r: int, g: int, b: int) -> str:
            return f"#{r:02x}{g:02x}{b:02x}"

        r1, g1, b1 = hex_to_rgb(BACKGROUND_GRADIENT_TOP)
        r2, g2, b2 = hex_to_rgb(BACKGROUND_GRADIENT_BOTTOM)

        for i in range(BACKGROUND_STEPS):
            t = i / max(1, BACKGROUND_STEPS - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            color = rgb_to_hex(r, g, b)
            y0 = int((WINDOW_HEIGHT / BACKGROUND_STEPS) * i)
            y1 = int((WINDOW_HEIGHT / BACKGROUND_STEPS) * (i + 1))
            self.canvas.create_rectangle(0, y0, WINDOW_WIDTH, y1, fill=color, outline=color)

    def _draw_title(self):
        """
        Pixel-art styled title using blocky font and shadow for an 8-bit feel.
        """
        title = "Fall Catcher"
        x = WINDOW_WIDTH // 2
        y = 180
        # Shadow layers for pixel feel
        for dx, dy, color in ((4, 4, "#5a3110"), (2, 2, "#7a4014")):
            self.canvas.create_text(x + dx, y + dy, text=title, fill=color, font=("Courier New", 36, "bold"), anchor="c")
        # Main text
        self.canvas.create_text(x, y, text=title, fill="#ffd9a0", font=("Courier New", 36, "bold"), anchor="c")

        # Subtitle
        self.canvas.create_text(
            x, y + 48,
            text="A cozy leaf-catching game",
            fill="#6b4b2a",
            font=("Courier New", 14, "bold"),
            anchor="c"
        )

    def _draw_play_button(self):
        """
        Draw a pixel-art styled 'PLAY' button using canvas rectangles and text.
        Returns the bbox tuple for click hit-testing.
        """
        btn_w, btn_h = 220, 64
        x = (WINDOW_WIDTH - btn_w) // 2
        y = WINDOW_HEIGHT // 2 + 40

        # Outer border (dark)
        self.canvas.create_rectangle(x, y, x + btn_w, y + btn_h, fill="#5a3110", outline="#5a3110")
        # Inner border (mid)
        self.canvas.create_rectangle(x + 4, y + 4, x + btn_w - 4, y + btn_h - 4, fill="#8b4f1f", outline="#8b4f1f")
        # Button face
        self.canvas.create_rectangle(x + 8, y + 8, x + btn_w - 8, y + btn_h - 8, fill="#d9883d", outline="#d9883d")
        # Pixel highlight
        self.canvas.create_rectangle(x + 8, y + 8, x + btn_w - 8, y + 20, fill="#f6b26b", outline="#f6b26b")

        self.canvas.create_text(
            x + btn_w // 2, y + btn_h // 2 + 2,
            text="PLAY",
            fill="#3b2618",
            font=("Courier New", 20, "bold"),
            anchor="c"
        )
        return (x, y, x + btn_w, y + btn_h)

    def _draw_pixel_leaf_art(self, x: int, y: int, scale: int = 5):
        """
        Draw a simple pixel-art leaf made of colored squares.
        """
        pixels = [
            "..GGG.",
            ".GGOGG",
            "GOOOOG",
            ".GGOGG",
            "..GGG.",
        ]
        colors = {"G": "#c4661a", "O": "#e6954b", ".": None}
        for r, row in enumerate(pixels):
            for c, ch in enumerate(row):
                color = colors.get(ch)
                if not color:
                    continue
                px = x + c * scale
                py = y + r * scale
                self.canvas.create_rectangle(px, py, px + scale, py + scale, fill=color, outline=color)

    # ----------------------------
    # Events
    # ----------------------------

    def _on_click(self, event):
        x1, y1, x2, y2 = self._play_btn_bbox
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            if callable(self.on_play):
                self.on_play()