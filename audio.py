import os
import sys
from concurrent.futures import ThreadPoolExecutor

from gtts import gTTS as gtts
from mutagen import MutagenError
from mutagen.mp3 import MP3
from PyQt5.QtWidgets import QApplication

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pygame import mixer
from pygame.mixer import music

app = QApplication(sys.argv)

if not mixer.get_init():
    mixer.init()


def play(audio_path: str) -> None:
    music.load(audio_path)
    music.play()


def beep():
    app.beep()


def check_and_delete(file_path: str) -> bool:
    try:
        MP3(file_path)
        return False
    except MutagenError:
        print(f"⚠️ {file_path} is not a valid MP3 file, deleting...")
        os.remove(file_path)
        return True


def delete_invalid_mp3(audio_dir: str) -> int:
    file_paths = []

    for root, _, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(".mp3"):
                file_paths.append(os.path.join(root, file))

    with ThreadPoolExecutor(max_workers=32) as executor:
        results = list(executor.map(check_and_delete, file_paths))

    return sum(results)


def generate(word: str, path: str) -> bool:
    try:
        tts = gtts(text=word, lang="en")
        tts.save(path)
    except Exception as e:
        print(f'⚠️ generate audio "{word}" failed. Error: {e}')
        return False
    print(f'💿 finish generate audio "{word}" to "{path}".')
    return True
