import os

import mutagen
import mutagen.mp3
from gtts import gTTS as gtts
from pygame import mixer


def init(audio_dir: str):
    mixer.init()

    for root, _, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    mutagen.mp3.MP3(file_path)
                except mutagen.MutagenError:
                    print(f"⚠️ {file} is not a valid MP3 file, deleting...")
                    os.remove(file_path)


def generate(word: str, path: str):
    if not os.path.exists(path):
        tts = gtts(text=word, lang="en")
        tts.save(path)
        print(f'💿 finish generate audio "{word}" to "{path}".')


def play(audio_path: str):
    mixer.music.load(audio_path)
    mixer.music.play()
