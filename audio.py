import os
import threading
from concurrent.futures import ThreadPoolExecutor

from gtts import gTTS as gtts
from mutagen import MutagenError
from mutagen.mp3 import MP3
from pygame import mixer

threading.Thread(mixer.init()).start()


def check_and_delete(file_path):
    try:
        MP3(file_path)
        return False
    except MutagenError:
        print(f"⚠️ {file_path} is not a valid MP3 file, deleting...")
        os.remove(file_path)
        return True


def delete_invalid_mp3(audio_dir: str):
    file_paths = []

    for root, _, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(".mp3"):
                file_paths.append(os.path.join(root, file))

    with ThreadPoolExecutor(max_workers=32) as executor:
        results = list(executor.map(check_and_delete, file_paths))

    return sum(results)


def generate(word: str, path: str):
    try:
        tts = gtts(text=word, lang="en")
        tts.save(path)
    except Exception as e:
        print(f'⚠️ generate audio "{word}" failed. Error: {e}')
        return False
    print(f'💿 finish generate audio "{word}" to "{path}".')
    return True


def play(audio_path: str):
    mixer.music.load(audio_path)
    mixer.music.play()
