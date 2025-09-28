import logging
from tkinter import Tk
from controllers.game_controller import GameController
from models.game_state import GameState
from views.game_view import GameView
from views.menu_view import MenuView
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    STREAM_AUDIO_URL, YOUTUBE_AUDIO_URL, BACKGROUND_MUSIC_PATH
)
from utils.audio import (
    play_stream_url, play_youtube_stream,
    play_youtube_audio, play_local_music_loop,
    prepare_youtube_stream, play_prepared_stream, get_prepared_stream_url
)

def _looks_like_youtube(url: str) -> bool:
    return any(host in url for host in ("youtube.com", "youtu.be"))

def main():
    # Basic logging to console
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger("leaf_catcher.app")

    root = Tk()
    root.title("Fall Catcher")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)

    # Create menu first; prepare audio while user is on the menu
    def on_play_clicked():
        # Start music only now
        if STREAM_AUDIO_URL:
            if _looks_like_youtube(STREAM_AUDIO_URL):
                # If already prepared, use it; else resolve+play directly
                if not play_prepared_stream():
                    logger.info("Prepared stream not ready; resolving+playing YouTube now...")
                    play_youtube_stream(STREAM_AUDIO_URL)
            else:
                play_stream_url(STREAM_AUDIO_URL)
        elif YOUTUBE_AUDIO_URL:
            # Prefer streaming from YouTube as well (no download) after click
            if not play_prepared_stream():
                logger.info("Prepared stream not ready; resolving+playing YouTube now...")
                play_youtube_stream(YOUTUBE_AUDIO_URL)
        else:
            # Fallback to local file if present
            try:
                import os
                if os.path.exists(BACKGROUND_MUSIC_PATH):
                    logger.info("Playing local background music: %s", BACKGROUND_MUSIC_PATH)
                    play_local_music_loop(BACKGROUND_MUSIC_PATH)
                else:
                    logger.info("No background music configured.")
            except Exception as e:
                logger.warning("Error while attempting to play local music: %s", e)

        # Remove menu and start game
        menu.destroy()
        game_state = GameState()
        game_view = GameView(root, game_state)
        game_controller = GameController(game_state, game_view)
        game_controller.start_game(root)

    # Show menu
    menu = MenuView(root, on_play=on_play_clicked)

    # Prepare audio stream while on menu (no playback yet)
    if STREAM_AUDIO_URL and _looks_like_youtube(STREAM_AUDIO_URL):
        logger.info("Preparing YouTube stream while on menu...")
        prepare_youtube_stream(STREAM_AUDIO_URL)
    elif not STREAM_AUDIO_URL and YOUTUBE_AUDIO_URL and _looks_like_youtube(YOUTUBE_AUDIO_URL):
        logger.info("Preparing YouTube stream while on menu (fallback URL)...")
        prepare_youtube_stream(YOUTUBE_AUDIO_URL)
    else:
        # Non-YouTube streams don't need preparation
        if STREAM_AUDIO_URL:
            logger.info("Streaming URL configured (non-YouTube). Will start on Play.")

    root.mainloop()

if __name__ == "__main__":
    main()