import torch
from scipy.spatial.distance import cosine
from transformers import BertModel, BertTokenizer

from common.cache import cache

tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
model = BertModel.from_pretrained("bert-base-chinese")


@cache
def load_embedding(word):
    inputs = tokenizer(word, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()


def semantic_similarity(word1, word2):
    word1_splits = word1.split("，")
    word2_splits = word2.split("，")

    max_similarity = 0.0
    for w1 in word1_splits:
        for w2 in word2_splits:
            embedding1 = load_embedding(w1)
            embedding2 = load_embedding(w2)
            similarity = 1 - cosine(embedding1, embedding2)
            max_similarity = max(similarity, max_similarity)

    return max_similarity
