from Levenshtein import editops

VOWELS = set("aeiou")
CONSONANTS = set("bcdfghjklmnpqrstvwxyz")


def get_replace_cost(u_char: str, a_char: str):
    if u_char in VOWELS and a_char in VOWELS:
        return 0.5
    elif u_char in CONSONANTS and a_char in CONSONANTS:
        return 0.8
    else:
        return 1.0


def weighted_ratio(user_answer, answer):
    ops = editops(user_answer, answer)
    total_cost = 0

    for op, i, j in ops:
        if op == "replace":
            total_cost += get_replace_cost(user_answer[i], answer[j])
        else:
            total_cost += 1

    max_len = max(len(user_answer), len(answer))
    return 1 - total_cost / max_len


def compare_answer(user_answer, answer) -> bool:
    user_answer = " ".join(user_answer.strip(" \u3000").lower().split())
    answer = " ".join(answer.strip(" \u3000").lower().split())
    is_correct = user_answer == answer

    similarity = weighted_ratio(user_answer, answer) * 100
    e = "✅" if is_correct else "❌"

    print(f"{e} | {answer} | {user_answer} | {similarity:.2f}%")
    return is_correct
