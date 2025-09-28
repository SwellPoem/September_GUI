from utils.constants import (
    WINDOW_WIDTH, BASKET_WIDTH, BASKET_HEIGHT, BASKET_SPEED
)

class Basket:
    def __init__(self):
        self.width = BASKET_WIDTH
        self.height = BASKET_HEIGHT
        self.speed = BASKET_SPEED
        self.x = (WINDOW_WIDTH - self.width) // 2
        self.y = 0  # Will be set based on window height by view/controller

    def rect(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def move_left(self):
        self.x = max(0, self.x - self.speed)

    def move_right(self, canvas_width: int):
        self.x = min(canvas_width - self.width, self.x + self.speed)