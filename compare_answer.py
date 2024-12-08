from Levenshtein import editops, ratio
from termcolor import colored


def compare_answer(user_answer, answer) -> bool:
    user_answer = " ".join(user_answer.strip(" \u3000").lower().split())
    answer = " ".join(answer.strip(" \u3000").lower().split())

    similarity = ratio(user_answer, answer) * 100
    is_correct = user_answer == answer
    e = "✅" if is_correct else "❌"

    print(f"{e} | {answer} | {user_answer} | {similarity:.2f}%")
    return is_correct
