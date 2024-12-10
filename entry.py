import os
import re
from functools import cached_property, lru_cache

import nltk
from nltk import pos_tag

from config import audio_dir

nltk.download("averaged_perceptron_tagger", quiet=True)
nltk.download("averaged_perceptron_tagger_eng", quiet=True)

POS_MAPPING = {
    "NN": "n.",
    "NNS": "n.",
    "VB": "v.",
    "VBD": "v.",
    "VBG": "v.",
    "VBN": "v.",
    "VBP": "v.",
    "VBZ": "v.",
    "JJ": "adj.",
    "JJR": "adj.",
    "JJS": "adj.",
    "RB": "adv.",
    "RBR": "adv.",
    "RBS": "adv.",
}


@lru_cache(maxsize=None)
def get_pos(word: str) -> str:
    tagged = pos_tag([word])
    pos = []
    for tag in tagged:
        if tag[1] in POS_MAPPING:
            pos.append(POS_MAPPING[tag[1]])
    return ", ".join(pos)


delimiters = r"[,/;；。 \u3000]"


class Entry:
    def __init__(self, line: str):
        self._english = ""
        self._chinese = ""

        chinese_words = []
        english_words = []

        for word in re.split(delimiters, line):
            if word.isascii() and word.strip():
                english_words.append(word)
            elif word.strip():
                chinese_words.append(word)

        self._english = " ".join(english_words)
        self._chinese = "，".join(chinese_words)

    @property
    def english(self):
        return self._english

    @property
    def chinese(self):
        return self._chinese

    @cached_property
    def is_phrase(self) -> bool:
        return self.english.count(" ") > 0

    @cached_property
    def audio_path(self) -> str:
        return os.path.join(audio_dir, f"{self.english}.mp3")

    @cached_property
    def pos(self) -> str:
        return get_pos(self.english)

    @cached_property
    def lower_english(self) -> str:
        return self.english.lower()

    def __str__(self):
        return self.english + " " + self.pos + " " + self.chinese
