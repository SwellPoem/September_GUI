from typing import List
from models.leaf import Leaf
from models.basket import Basket
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT

class GameState:
    def __init__(self):
        self.score = 0
        self.leaves: List[Leaf] = []
        self.basket = Basket()
        # Position basket near bottom
        self.basket.y = WINDOW_HEIGHT - self.basket.height - 20

        # For tests compatibility
        self.basket_position = self.basket.x

    def update_score(self, points):
        self.score += points

    def add_leaf(self, leaf: Leaf):
        self.leaves.append(leaf)

    def remove_leaf(self, leaf: Leaf):
        if leaf in self.leaves:
            self.leaves.remove(leaf)

    def set_basket_position(self, position):
        self.basket.x = position
        self.basket_position = position  # keep both in sync

    def reset(self):
        self.score = 0
        self.leaves.clear()
        self.basket.x = (WINDOW_WIDTH - self.basket.width) // 2
        self.basket.y = WINDOW_HEIGHT - self.basket.height - 20
        self.basket_position = self.basket.x

    def get_game_state(self):
        return {
            'score': self.score,
            'leaves': self.leaves,
            'basket_position': self.basket_position
        }