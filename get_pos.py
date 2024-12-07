import nltk
from nltk import pos_tag

from cache import cache

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


@cache
def get_pos(word: str) -> str:
    tagged = pos_tag([word])

    pos = ""
    for pos_tagged in tagged:
        if POS_MAPPING.get(pos_tagged[1], None) is not None:
            pos += POS_MAPPING[pos_tagged[1]] + ", "

    return pos.strip(", ")
