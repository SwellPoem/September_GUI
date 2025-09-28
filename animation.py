import random
import config
from PIL import Image, ImageTk

class LeafAnimator:
    def __init__(self, window, canvas):
        self.window = window
        self.canvas = canvas
        self.leaves = []
        self.leaf_img = None
        self._load_images()
        self.spawn_leaves()
        self.animate_leaves()

    def _load_images(self):
        try:
            leaf_img_raw = Image.open(config.LEAF_IMG_PATH).resize((32, 32))
            self.leaf_img = ImageTk.PhotoImage(leaf_img_raw)
            self.canvas.leaf_img = self.leaf_img  # Prevent garbage collection
        except Exception as e:
            self.leaf_img = None
            print("No leaf image found, will use ovals:", e)

    def spawn_leaves(self):
        self.leaves = []
        for _ in range(config.NUM_LEAVES):
            x = random.randint(0, config.CANVAS_WIDTH - 32)
            y = random.randint(-100, config.CANVAS_HEIGHT - 50)
            speed = random.uniform(1, 3)
            swing = random.uniform(0.5, 2)
            self.leaves.append({'x': x, 'y': y, 'speed': speed, 'swing': swing, 'angle': random.uniform(0, 6.28)})

    def animate_leaves(self):
        self.canvas.delete("leaf")  # ONLY delete leaves
        for leaf in self.leaves:
            leaf['y'] += leaf['speed']
            leaf['x'] += random.uniform(-leaf['swing'], leaf['swing'])
            leaf['angle'] += 0.03
            if leaf['y'] > config.CANVAS_HEIGHT:
                leaf['y'] = random.randint(-50, 0)
                leaf['x'] = random.randint(0, config.CANVAS_WIDTH - 32)
            if self.leaf_img:
                self.canvas.create_image(leaf['x'], leaf['y'], image=self.leaf_img, anchor="nw", tags="leaf")
            else:
                self.canvas.create_oval(leaf['x'], leaf['y'], leaf['x'] + 20, leaf['y'] + 10, fill="#b9a394", outline="", tags="leaf")
        self.window.after(50, self.animate_leaves)