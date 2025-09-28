import os
import threading
import tempfile
import shutil
import logging
import traceback
from typing import Optional

logger = logging.getLogger("leaf_catcher.audio")

# pygame for local file playback (downloaded mp3 or local assets)
try:
    import pygame  # type: ignore
except Exception:
    pygame = None

# yt-dlp to resolve YouTube URLs (for streaming or download)
try:
    import yt_dlp  # type: ignore
except Exception:
    yt_dlp = None

# python-vlc for streaming URLs (http/https) including YouTube resolved streams
try:
    import vlc  # type: ignore
except Exception:
    vlc = None

_current_music_path: Optional[str] = None
_ffmpeg_exe: Optional[str] = None
_vlc_instance: Optional["vlc.Instance"] = None  # type: ignore
_vlc_player: Optional["vlc.MediaPlayer"] = None  # type: ignore

# Prepared stream URL (resolved ahead of time while in menu)
_prepared_stream_url: Optional[str] = None
_prepare_thread: Optional[threading.Thread] = None


def _ensure_pygame() -> bool:
    """
    Ensure pygame.mixer is initialized.
    Tries default driver, then falls back to SDL_AUDIODRIVER=dummy if needed.
    """
    if pygame is None:
        logger.error("pygame is not installed. Background audio via pygame disabled.")
        return False

    try:
        if not pygame.mixer.get_init():
            logger.info("Initializing pygame.mixer with default audio driver...")
            pygame.mixer.init()
            logger.info("pygame.mixer initialized (default).")
        return True
    except Exception as e:
        logger.warning("Default audio driver init failed: %s", e)
        try:
            if not os.environ.get("SDL_AUDIODRIVER"):
                os.environ["SDL_AUDIODRIVER"] = "dummy"
                logger.info("Retrying pygame.mixer init with SDL_AUDIODRIVER=dummy...")
            pygame.mixer.init()
            logger.info("pygame.mixer initialized with dummy driver.")
            return True
        except Exception as e2:
            logger.error("Failed to initialize pygame.mixer: %s", e2)
            logger.debug("Traceback:\n%s", traceback.format_exc())
            return False


def _ensure_vlc() -> bool:
    """
    Ensure python-vlc (libVLC) is available and ready.
    On macOS, make sure VLC.app is installed or libvlc is available.
    """
    global _vlc_instance, _vlc_player
    if vlc is None:
        logger.error("python-vlc is not installed. Install 'python-vlc' and VLC to enable streaming.")
        return False
    try:
        if _vlc_instance is None:
            logger.info("Creating VLC instance...")
            _vlc_instance = vlc.Instance()  # can pass custom args if needed
        if _vlc_player is None:
            _vlc_player = _vlc_instance.media_player_new()
        return True
    except Exception as e:
        logger.error("Failed to initialize VLC (libvlc). Ensure VLC is installed. Error: %s", e)
        logger.debug("Traceback:\n%s", traceback.format_exc())
        return False


def _stop_vlc():
    global _vlc_player
    try:
        if _vlc_player is not None:
            _vlc_player.stop()
            logger.info("VLC stream stopped.")
    except Exception as e:
        logger.debug("Ignoring VLC stop error: %s", e)


def _locate_ffmpeg() -> Optional[str]:
    """
    Try to locate an ffmpeg executable.
    Order:
    1) PATH (ffmpeg / ffmpeg.exe)
    2) IMAGEIO_FFMPEG_EXE env var
    3) imageio-ffmpeg bundled binary
    """
    for name in ("ffmpeg", "ffmpeg.exe"):
        found = shutil.which(name)
        if found:
            logger.info("Found ffmpeg on PATH: %s", found)
            return found

    env_path = os.environ.get("IMAGEIO_FFMPEG_EXE")
    if env_path and os.path.exists(env_path):
        logger.info("Found ffmpeg via IMAGEIO_FFMPEG_EXE: %s", env_path)
        return env_path

    try:
        import imageio_ffmpeg  # type: ignore
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            logger.info("Found ffmpeg via imageio-ffmpeg: %s", path)
            return path
    except Exception as e:
        logger.debug("imageio-ffmpeg not available or failed to provide ffmpeg: %s", e)

    return None


def _ffmpeg_available() -> bool:
    """
    Resolve and cache ffmpeg path, logging guidance if not found.
    """
    global _ffmpeg_exe
    if _ffmpeg_exe and os.path.exists(_ffmpeg_exe):
        return True

    _ffmpeg_exe = _locate_ffmpeg()
    if _ffmpeg_exe:
        return True

    logger.error(
        "ffmpeg not found. Install one of the following or add ffmpeg to PATH:\n"
        "- System ffmpeg (recommended)\n"
        "- pip install imageio-ffmpeg (bundled binary)\n"
        "If installed via imageio-ffmpeg, we auto-detect it. Otherwise set IMAGEIO_FFMPEG_EXE env var."
    )
    return False


def _ffmpeg_location_for_ydl() -> Optional[str]:
    """
    Return a value suitable for yt-dlp 'ffmpeg_location' option.
    """
    if not _ffmpeg_exe:
        return None
    return os.path.dirname(_ffmpeg_exe) or _ffmpeg_exe


def stop_music() -> None:
    """
    Stop any playback (pygame or VLC).
    """
    if pygame and pygame.mixer.get_init():
        try:
            pygame.mixer.music.stop()
            logger.info("Pygame music stopped.")
        except Exception as e:
            logger.debug("Ignoring pygame stop error: %s", e)
    _stop_vlc()


def play_local_music_loop(path: str) -> None:
    """
    Play a local audio file in a loop using pygame.
    Supports common formats supported by pygame (mp3/ogg/wav).
    """
    stop_music()
    if not _ensure_pygame():
        return
    if not os.path.exists(path):
        logger.error("Local music file not found: %s", os.path.abspath(path))
        return
    try:
        logger.info("Loading local music: %s", os.path.abspath(path))
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
        logger.info("Local music playing in loop.")
    except Exception as e:
        logger.error("Failed to play local music: %s", e)
        logger.debug("Traceback:\n%s", traceback.format_exc())


def play_stream_url(url: str) -> None:
    """
    Stream an online audio URL directly via VLC (no download).
    Supports many formats and live radio streams.
    """
    stop_music()
    if not url:
        logger.warning("Empty stream URL. Skipping.")
        return
    if not _ensure_vlc():
        logger.error("VLC unavailable. Cannot stream: %s", url)
        return
    try:
        assert _vlc_instance is not None and _vlc_player is not None
        logger.info("Starting VLC stream: %s", url)
        media = _vlc_instance.media_new(url)
        _vlc_player.set_media(media)
        _vlc_player.play()
        logger.info("Streaming started (VLC).")
    except Exception as e:
        logger.error("Failed to stream URL via VLC: %s", e)
        logger.debug("Traceback:\n%s", traceback.format_exc())


def prepare_youtube_stream(url: str) -> None:
    """
    Resolve a YouTube URL to a direct audio stream URL in the background (no playback).
    Stores the URL for later playback via play_prepared_stream().
    """
    global _prepared_stream_url, _prepare_thread
    if not yt_dlp:
        logger.error("yt-dlp is not installed. Cannot resolve YouTube.")
        return

    def worker():
        global _prepared_stream_url
        try:
            logger.info("Resolving YouTube stream URL via yt-dlp (prepare only): %s", url)
            ydl_opts = {
                "quiet": True,
                "no_warnings": False,
                "skip_download": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            stream_url = None
            formats = info.get("formats") or []
            audio_formats = [
                f for f in formats
                if f.get("vcodec") in (None, "none") and f.get("acodec") not in (None, "none") and f.get("url")
            ]
            if audio_formats:
                audio_formats.sort(key=lambda f: f.get("abr") or 0, reverse=True)
                stream_url = audio_formats[0]["url"]
            if not stream_url:
                stream_url = info.get("url")
            if not stream_url:
                logger.error("Failed to resolve a direct audio stream URL for YouTube.")
                return
            _prepared_stream_url = stream_url
            logger.info("YouTube stream prepared.")
        except Exception as e:
            logger.error("Failed to resolve YouTube stream: %s", e)
            logger.debug("Traceback:\n%s", traceback.format_exc())

    # Avoid spawning multiple resolve threads
    if _prepare_thread and _prepare_thread.is_alive():
        logger.info("YouTube stream resolution already in progress.")
        return
    _prepare_thread = threading.Thread(target=worker, daemon=True)
    _prepare_thread.start()


def get_prepared_stream_url() -> Optional[str]:
    return _prepared_stream_url


def play_prepared_stream() -> bool:
    """
    If a stream URL was prepared, start playback via VLC.
    Returns True if playback started, False otherwise.
    """
    url = _prepared_stream_url
    if not url:
        logger.warning("No prepared stream URL to play.")
        return False
    play_stream_url(url)
    return True


def play_youtube_stream(url: str) -> None:
    """
    Resolve a YouTube URL to a direct audio stream and play via VLC.
    Requires yt-dlp. No file is downloaded; playback is from the resolved URL.
    """
    stop_music()
    if not yt_dlp:
        logger.error("yt-dlp is not installed. Cannot stream YouTube.")
        return
    if not _ensure_vlc():
        logger.error("VLC unavailable. Cannot stream YouTube: %s", url)
        return

    def worker():
        try:
            logger.info("Resolving YouTube stream URL via yt-dlp (no download): %s", url)
            ydl_opts = {
                "quiet": True,
                "no_warnings": False,
                "skip_download": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            stream_url = None
            formats = info.get("formats") or []
            audio_formats = [
                f for f in formats
                if f.get("vcodec") in (None, "none") and f.get("acodec") not in (None, "none") and f.get("url")
            ]
            if audio_formats:
                audio_formats.sort(key=lambda f: f.get("abr") or 0, reverse=True)
                stream_url = audio_formats[0]["url"]
            if not stream_url:
                stream_url = info.get("url")
            if not stream_url:
                logger.error("Failed to resolve a direct audio stream URL for YouTube.")
                return

            logger.info("Resolved YouTube audio stream. Handing off to VLC...")
            play_stream_url(stream_url)
        except Exception as e:
            logger.error("Failed to resolve/play YouTube stream: %s", e)
            logger.debug("Traceback:\n%s", traceback.format_exc())

    threading.Thread(target=worker, daemon=True).start()


def play_youtube_audio(url: str) -> None:
    """
    Download and play YouTube audio (mp3) in a background thread.
    Requires yt-dlp and ffmpeg.
    """
    stop_music()
    if not url:
        logger.warning("No YOUTUBE_AUDIO_URL configured. Skipping YouTube audio.")
        return
    if yt_dlp is None:
        logger.error("yt-dlp is not installed. Install it to enable YouTube audio.")
        return
    if not _ffmpeg_available():
        return

    def worker():
        global _current_music_path
        if not _ensure_pygame():
            return
        tmpdir = None
        try:
            tmpdir = tempfile.mkdtemp(prefix="leaf_catcher_")
            outtmpl = os.path.join(tmpdir, "bgm.%(ext)s")

            ff_loc = _ffmpeg_location_for_ydl()
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": False,
                "ffmpeg_location": ff_loc,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

            logger.info("Starting YouTube audio download: %s", url)
            logger.info("Using ffmpeg at: %s", _ffmpeg_exe)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info("YouTube download complete. Searching for extracted mp3...")

            mp3_path = None
            for name in os.listdir(tmpdir):
                if name.lower().endswith(".mp3"):
                    mp3_path = os.path.join(tmpdir, name)
                    break
            if not mp3_path:
                logger.error("No mp3 file produced after download. Check ffmpeg installation.")
                return

            logger.info("Playing downloaded mp3: %s", os.path.abspath(mp3_path))
            _current_music_path = mp3_path
            pygame.mixer.music.load(mp3_path)
            pygame.mixer.music.play(-1)
            logger.info("YouTube audio playing in loop.")
        except Exception as e:
            logger.error("Failed to download/play YouTube audio: %s", e)
            logger.debug("Traceback:\n%s", traceback.format_exc())
        finally:
            if tmpdir:
                logger.debug("Temporary download directory: %s", tmpdir)
    threading.Thread(target=worker, daemon=True).start()