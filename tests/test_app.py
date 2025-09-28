import unittest
from src.controllers.game_controller import GameController
from src.models.game_state import GameState

class TestGameController(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.controller = GameController(self.game_state)

    def test_spawn_leaf(self):
        initial_leaf_count = len(self.game_state.leaves)
        self.controller.spawn_leaf()
        self.assertEqual(len(self.game_state.leaves), initial_leaf_count + 1)

    def test_update_score(self):
        self.game_state.score = 0
        self.controller.update_score(10)
        self.assertEqual(self.game_state.score, 10)

    def test_basket_movement(self):
        initial_position = self.game_state.basket_position
        self.controller.move_basket('left')
        self.assertNotEqual(self.game_state.basket_position, initial_position)

if __name__ == '__main__':
    unittest.main()