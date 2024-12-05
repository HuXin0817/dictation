import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pygame import mixer
from pygame.mixer import Sound

if not mixer.get_init():
    mixer.init()

audio_cache = {}


def cache(audio_path: str) -> Sound:
    if audio_path not in audio_cache:
        try:
            audio_cache[audio_path] = mixer.Sound(audio_path)
        except Exception as e:
            raise ValueError(f"Failed to load audio file: {audio_path}, Error: {e}")
    return audio_cache[audio_path]


def play(audio_path: str) -> None:
    try:
        sound = cache(audio_path)
        sound.play()
    except Exception as e:
        print(f"Failed to play audio: {audio_path}, Error: {e}")
