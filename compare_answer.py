import Levenshtein


def compare_answer(user_answer, answer) -> bool:
    user_answer = " ".join(user_answer.strip(" \u3000").lower().split())
    answer = " ".join(answer.strip(" \u3000").lower().split())

    if user_answer == answer:
        return True

    similarity = Levenshtein.ratio(user_answer, answer)
    print(f"❌ | {answer} | {user_answer} | similarity: {100 * similarity:.2f}%")
    return False
