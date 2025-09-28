# Constants used throughout the application
from pathlib import Path

# Resolve project directories relative to this file, robust to CWD
THIS_FILE = Path(__file__).resolve()
SRC_DIR = THIS_FILE.parents[1]
PROJECT_ROOT = THIS_FILE.parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# Window size (requirement: 600x800)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

# Cozy September vibe colors (warm palette)
BACKGROUND_GRADIENT_TOP = "#FCE5CD"    # light pumpkin
BACKGROUND_GRADIENT_BOTTOM = "#FFD7A8" # warm amber
BACKGROUND_STEPS = 32
# 20% darker factor for background image/gradient
BACKGROUND_DARKEN_FACTOR = 0.6

# Colors
LEAF_COLOR = "#D2691E"   # chocolate
BASKET_COLOR = "#8B4513" # saddle brown
SCORE_TEXT_COLOR = "#5A3E2B"

# Leaf properties
LEAF_MIN_SPEED = 2
LEAF_MAX_SPEED = 6
LEAF_SIZE = 40  # bigger leaves

# Basket properties
BASKET_WIDTH = 100
BASKET_HEIGHT = 20
BASKET_SPEED = 15

# Scoring
SCORE_INCREMENT = 1

# Spawn/loop
TICK_MS = 16                # ~60 FPS
SPAWN_INTERVAL_MS = 700     # one leaf roughly every 0.7s

# File paths for assets (absolute paths)
LEAF_IMAGE_PATH = str(IMAGES_DIR / "leaf.png")
BACKGROUND_IMAGE_PATH = str(IMAGES_DIR / "background.png")
BASKET_IMAGE_PATH = str(IMAGES_DIR / "basket.png")          # optional, may not exist
BACKGROUND_MUSIC_PATH = str(SOUNDS_DIR / "background.mp3")  # Optional local fallback
CATCH_SOUND_PATH = str(SOUNDS_DIR / "catch.wav")            # Optional

# Streaming music URL (preferred). Example: an online mp3/ogg stream, internet radio, or a direct file URL.
STREAM_AUDIO_URL = "https://www.youtube.com/watch?v=M0lVOhvJajc"  # e.g., "https://stream.example.com/radio.mp3" or a YouTube link (we'll stream via VLC)

# Optional YouTube background music URL. If STREAM_AUDIO_URL is empty, this is used (download+play by default).
YOUTUBE_AUDIO_URL = "https://www.youtube.com/watch?v=M0lVOhvJajc"