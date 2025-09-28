from tkinter import Canvas, Label
from typing import Optional, Tuple
import os

# Pillow is optional; images will gracefully fall back if not available
try:
    from PIL import Image, ImageTk  # type: ignore
    from PIL import ImageEnhance  # type: ignore
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    ImageEnhance = None  # type: ignore

from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BACKGROUND_GRADIENT_TOP, BACKGROUND_GRADIENT_BOTTOM, BACKGROUND_STEPS,
    BASKET_COLOR, SCORE_TEXT_COLOR, LEAF_COLOR, LEAF_SIZE,
    LEAF_IMAGE_PATH, BACKGROUND_IMAGE_PATH, BASKET_IMAGE_PATH,
    BACKGROUND_DARKEN_FACTOR,
)


class GameView:
    """
    Tkinter view for the Leaf Catcher game.
    - Renders background (image if available, else warm gradient)
    - Renders basket (image if available, else rectangle)
    - Renders leaves (image if available, else oval)
    - Shows a real-time score label at the top-left
    """

    def __init__(self, master, game_state):
        self.master = master
        self.game_state = game_state

        # Main canvas for drawing the game
        self.canvas = Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=False)

        # Score label over the canvas
        self.score_label = Label(
            master,
            text=f"Score: {self.game_state.score}",
            font=("Arial", 18, "bold"),
            fg=SCORE_TEXT_COLOR
        )
        self.score_label.place(x=10, y=8)

        # Loaded images (or None if unavailable)
        self._leaf_photo: Optional[object] = None
        self._basket_photo: Optional[object] = None
        self._background_photo: Optional[object] = None
        self._load_images()

        # Track whether background is drawn to avoid redundant redraws
        self._bg_drawn = False

    # ----------------------------
    # Image loading helpers
    # ----------------------------

    def _load_single_image(self, label: str, path: str, size: Optional[Tuple[int, int]], brightness: float = 1.0) -> Optional[object]:
        """
        Log and load a single image. Prints the absolute path, existence, and
        success/failure messages. Returns a Tk PhotoImage or None.
        Applies optional brightness adjustment (for background darkening).
        """
        abs_path = os.path.abspath(path)
        print(f"[LeafCatcher] {label} image path: {abs_path}")

        if not os.path.exists(abs_path):
            print(f"[LeafCatcher][ERROR] {label} image not found at: {abs_path}")
            return None

        if Image is None or ImageTk is None:
            print(f"[LeafCatcher][WARN] Pillow not installed; cannot load {label} image. Falling back.")
            return None

        try:
            img = Image.open(abs_path).convert("RGBA")
            original_size = img.size
            if size:
                img = img.resize(size, Image.LANCZOS)
            # Apply darkening if requested
            if brightness != 1.0 and ImageEnhance is not None:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            photo = ImageTk.PhotoImage(img)
            print(f"[LeafCatcher][OK] Loaded {label} image. Original size: {original_size}, Display size: {size or original_size}, Brightness: {brightness}")
            return photo
        except Exception as e:
            print(f"[LeafCatcher][ERROR] Failed to load {label} image from {abs_path}: {e}")
            return None

    def _load_images(self) -> None:
        """
        Load all assets. Missing images will simply result in None,
        and draw fallbacks will be used instead.
        Always logs absolute paths and outcomes.
        """
        # Background image: scaled to full window size and darkened by 20%
        self._background_photo = self._load_single_image(
            "Background", BACKGROUND_IMAGE_PATH, (WINDOW_WIDTH, WINDOW_HEIGHT), brightness=BACKGROUND_DARKEN_FACTOR
        )
        # Basket image: scaled to basket size
        self._basket_photo = self._load_single_image(
            "Basket", BASKET_IMAGE_PATH, (self.game_state.basket.width, self.game_state.basket.height)
        )
        # Leaf image: scaled to leaf size (bigger leaves)
        self._leaf_photo = self._load_single_image(
            "Leaf", LEAF_IMAGE_PATH, (LEAF_SIZE, LEAF_SIZE)
        )

    # ----------------------------
    # Drawing functions
    # ----------------------------

    def draw_gradient_background(self) -> None:
        """
        Draw a cozy warm vertical gradient as a fallback background,
        darkened by BACKGROUND_DARKEN_FACTOR.
        """
        self.canvas.delete("bg")

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
            # Apply 20% darkening
            r = max(0, min(255, int(r * BACKGROUND_DARKEN_FACTOR)))
            g = max(0, min(255, int(g * BACKGROUND_DARKEN_FACTOR)))
            b = max(0, min(255, int(b * BACKGROUND_DARKEN_FACTOR)))
            color = rgb_to_hex(r, g, b)
            y0 = int((WINDOW_HEIGHT / BACKGROUND_STEPS) * i)
            y1 = int((WINDOW_HEIGHT / BACKGROUND_STEPS) * (i + 1))
            self.canvas.create_rectangle(0, y0, WINDOW_WIDTH, y1, fill=color, outline=color, tags="bg")

    def draw_background(self) -> None:
        """
        Prefer the provided background image; if missing/unavailable,
        draw the gradient fallback.
        """
        self.canvas.delete("bg")
        if self._background_photo:
            self.canvas.create_image(0, 0, image=self._background_photo, anchor="nw", tags="bg")
        else:
            self.draw_gradient_background()
        self._bg_drawn = True

    def draw_basket(self) -> None:
        """
        Draw the player basket using an image if available, else a rectangle.
        """
        self.canvas.delete("basket")
        bx, by = self.game_state.basket.x, self.game_state.basket.y
        if self._basket_photo:
            self.canvas.create_image(bx, by, image=self._basket_photo, anchor="nw", tags="basket")
        else:
            self.canvas.create_rectangle(
                bx, by,
                bx + self.game_state.basket.width, by + self.game_state.basket.height,
                fill=BASKET_COLOR, outline="", tags="basket"
            )

    def draw_leaves(self) -> None:
        """
        Draw all leaves. If a leaf image is available, use it; otherwise draw a colored oval.
        """
        self.canvas.delete("leaves")
        for leaf in self.game_state.leaves:
            # Attach the shared leaf image to each leaf if not set
            if self._leaf_photo and leaf.image is None:
                leaf.image = self._leaf_photo
            if leaf.image:
                self.canvas.create_image(leaf.x, leaf.y, image=leaf.image, anchor="nw", tags="leaves")
            else:
                # Fallback: simple oval
                self.canvas.create_oval(
                    leaf.x, leaf.y, leaf.x + leaf.size, leaf.y + leaf.size,
                    fill=LEAF_COLOR, outline="", tags="leaves"
                )

    # ----------------------------
    # UI updates
    # ----------------------------

    def update_score(self) -> None:
        self.score_label.config(text=f"Score: {self.game_state.score}")

    # Backward-compatible alias
    def update_score_display(self, _score) -> None:
        self.update_score()

    def render(self) -> None:
        """
        Render the full frame: background (first time), leaves, basket, and score.
        Called every tick by the controller.
        """
        if not self._bg_drawn:
            self.draw_background()
        self.draw_leaves()
        self.draw_basket()
        self.update_score()

    def reset_display(self) -> None:
        """
        Reset the canvas and redraw the background and score.
        Useful on game reset.
        """
        self.canvas.delete("all")
        self._bg_drawn = False
        self.draw_background()
        self.update_score()