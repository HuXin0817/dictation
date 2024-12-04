import os
import threading

import mutagen
import mutagen.mp3
from gtts import gTTS as gtts
from pygame import mixer


def init(audio_dir: str):
    threading.Thread(mixer.init()).start()
    delete_invalid_mp3(audio_dir)


def delete_invalid_mp3(audio_dir: str):
    n = 0
    for root, _, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    mutagen.mp3.MP3(file_path)
                except mutagen.MutagenError:
                    print(f"⚠️ {file} is not a valid MP3 file, deleting...")
                    os.remove(file_path)
                    n += 1
    return n


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
