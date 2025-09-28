from typing import Optional

class Leaf:
    def __init__(self, x: int, y: int, speed: int, size: int, color: str, image: Optional[object] = None):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.color = color
        self.image = image  # Tk PhotoImage or None

    def update(self):
        self.y += self.speed

    def bbox(self):
        # Return bounding box (left, top, right, bottom)
        return (self.x, self.y, self.x + self.size, self.y + self.size)