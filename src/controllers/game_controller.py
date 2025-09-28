import random
from typing import Optional

from models.game_state import GameState
from models.leaf import Leaf
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    LEAF_MIN_SPEED, LEAF_MAX_SPEED, LEAF_SIZE, LEAF_COLOR,
    SCORE_INCREMENT, TICK_MS, SPAWN_INTERVAL_MS
)

class GameController:
    def __init__(self, game_state: GameState, game_view: Optional[object] = None):
        self.game_state = game_state
        self.game_view = game_view
        self.root = getattr(game_view, "master", None)
        self._spawn_after_id = None
        self._loop_after_id = None

    # -- Game loop management --

    def start_game(self, root: Optional[object] = None):
        # Allow app to pass root explicitly
        if root is not None:
            self.root = root
        # Key bindings if we have a Tk root
        if self.root:
            self.root.bind("<Left>", lambda _e: self.move_basket('left'))
            self.root.bind("<Right>", lambda _e: self.move_basket('right'))
        # Mouse movement on canvas (move basket with mouse)
        if self.game_view and hasattr(self.game_view, "canvas") and self.game_view.canvas is not None:
            canvas = self.game_view.canvas
            canvas.bind("<Motion>", self._on_mouse_move)
            canvas.bind("<B1-Motion>", self._on_mouse_move)  # also allow dragging
        # Start loops
        self._schedule_spawn()
        self._schedule_tick()

    def _schedule_tick(self):
        if self.root:
            self._loop_after_id = self.root.after(TICK_MS, self._tick)

    def _schedule_spawn(self):
        if self.root:
            self._spawn_after_id = self.root.after(SPAWN_INTERVAL_MS, self._spawn_and_reschedule)

    def _spawn_and_reschedule(self):
        self.spawn_leaf()
        self._schedule_spawn()

    def _tick(self):
        self.update_game()
        self._schedule_tick()

    # -- Core logic --

    def spawn_leaf(self):
        x = random.randint(0, max(0, WINDOW_WIDTH - LEAF_SIZE))
        y = -LEAF_SIZE
        speed = random.randint(LEAF_MIN_SPEED, LEAF_MAX_SPEED)
        leaf = Leaf(x=x, y=y, speed=speed, size=LEAF_SIZE, color=LEAF_COLOR)
        self.game_state.add_leaf(leaf)

    def update_score(self, points):
        self.game_state.score += points
        if self.game_view:
            # Keep both available for compatibility
            if hasattr(self.game_view, "update_score_display"):
                self.game_view.update_score_display(self.game_state.score)
            else:
                self.game_view.update_score()

    def move_basket(self, direction):
        if direction == 'left':
            self.game_state.basket.move_left()
        elif direction == 'right':
            self.game_state.basket.move_right(WINDOW_WIDTH)
        # Keep tests-compatible attribute updated
        self.game_state.basket_position = self.game_state.basket.x

    def _on_mouse_move(self, event):
        """
        Center the basket on the mouse x-coordinate and clamp to canvas bounds.
        """
        half_w = self.game_state.basket.width // 2
        new_x = int(event.x - half_w)
        new_x = max(0, min(WINDOW_WIDTH - self.game_state.basket.width, new_x))
        self.game_state.basket.x = new_x
        self.game_state.basket_position = new_x  # keep tests-compatible attribute updated

    def update_game(self):
        # Update leaves positions
        to_remove = []
        for leaf in self.game_state.leaves:
            leaf.update()
            # Remove if off bottom
            if leaf.y > WINDOW_HEIGHT:
                to_remove.append(leaf)

        # Collision detection
        caught = self.check_collision()
        for leaf in to_remove:
            self.game_state.remove_leaf(leaf)

        # Update view
        if self.game_view:
            self.game_view.render()

        # Update score if any caught
        if caught:
            self.update_score(SCORE_INCREMENT * caught)

    def check_collision(self) -> int:
        # Return number of caught leaves
        bx1, by1, bx2, by2 = self.game_state.basket.rect()
        caught = 0
        remaining = []
        for leaf in self.game_state.leaves:
            lx1, ly1, lx2, ly2 = leaf.bbox()
            overlap = not (lx2 < bx1 or lx1 > bx2 or ly2 < by1 or ly1 > by2)
            if overlap and ly2 <= by2 + leaf.speed:  # caught near top of basket
                caught += 1
            else:
                remaining.append(leaf)
        self.game_state.leaves = remaining
        return caught

    def reset_game(self):
        self.game_state.reset()
        if self.game_view:
            self.game_view.reset_display()