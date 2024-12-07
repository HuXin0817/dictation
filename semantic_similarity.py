import threading

import torch
from scipy.spatial.distance import cosine
from transformers import BertModel, BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
model = BertModel.from_pretrained("bert-base-chinese")

cache = {}
cache_lock = threading.Lock()


def load_embedding(word):
    if word not in cache:
        inputs = tokenizer(word, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()

        with cache_lock:
            cache[word] = embedding

    return cache[word]


def semantic_similarity(word1, word2):
    embedding1 = load_embedding(word1)
    embedding2 = load_embedding(word2)

    return 1 - cosine(embedding1, embedding2)
