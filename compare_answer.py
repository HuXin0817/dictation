from Levenshtein import editops, ratio
from termcolor import colored


def compare_answer(user_answer, answer) -> bool:
    user_answer = " ".join(user_answer.strip(" \u3000").lower().split())
    answer = " ".join(answer.strip(" \u3000").lower().split())

    similarity = ratio(user_answer, answer) * 100
    is_correct = user_answer == answer
    e = "✅" if is_correct else "❌"

    operations = editops(user_answer, answer)
    user_chars = list(user_answer)
    answer_chars = list(answer)

    user_visual = []

    user_index, answer_index = 0, 0
    for op, i, j in operations:
        while user_index < i or answer_index < j:
            if (
                user_index < i
                and answer_index < j
                and user_chars[user_index] == answer_chars[answer_index]
            ):
                user_visual.append(user_chars[user_index])
                user_index += 1
                answer_index += 1
            elif user_index < i:
                user_visual.append(colored(user_chars[user_index], "red"))
                user_index += 1
            elif answer_index < j:
                answer_index += 1

        if op == "replace":
            user_visual.append(colored(user_chars[i], "yellow"))
            user_index += 1
            answer_index += 1
        elif op == "insert":
            answer_index += 1
            user_visual.append(colored(answer[i], "green"))
        elif op == "delete":
            user_visual.append(colored(user_chars[i], "red"))
            user_index += 1

    user_visual.extend(user_chars[user_index:])

    user_visual_str = "".join(user_visual)
    if not is_correct:
        user_answer += "=> " + user_visual_str
    print(f"{e} | {answer} | {user_answer} | {similarity:.3f}%")
    return is_correct
