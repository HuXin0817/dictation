import Levenshtein


def compare_answer(user_answer, answer) -> bool:
    user_answer = " ".join(user_answer.strip(" \u3000").lower().split())
    answer = " ".join(answer.strip(" \u3000").lower().split())

    right = user_answer == answer
    e = "✅" if right else "❌"
    similarity = Levenshtein.ratio(user_answer, answer) * 100

    print(f"{e} | {answer} | {user_answer} | {similarity:.2f}%")
    return right
