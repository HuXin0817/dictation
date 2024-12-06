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
    answer_visual = []

    user_index, answer_index = 0, 0
    for op, i, j in operations:
        while user_index < i or answer_index < j:
            if (
                user_index < i
                and answer_index < j
                and user_chars[user_index] == answer_chars[answer_index]
            ):
                user_visual.append(user_chars[user_index])
                answer_visual.append(answer_chars[answer_index])
                user_index += 1
                answer_index += 1
            elif user_index < i:
                user_visual.append(colored(user_chars[user_index], "red"))
                user_index += 1
            elif answer_index < j:
                answer_visual.append(colored(answer_chars[answer_index], "green"))
                answer_index += 1

        if op == "replace":
            user_visual.append(colored(user_chars[i], "yellow"))
            answer_visual.append(colored(answer_chars[j], "yellow"))
            user_index += 1
            answer_index += 1
        elif op == "insert":
            answer_visual.append(colored(answer_chars[j], "green"))
            answer_index += 1
        elif op == "delete":
            user_visual.append(colored(user_chars[i], "red"))
            user_index += 1

    user_visual.extend(user_chars[user_index:])
    answer_visual.extend(answer_chars[answer_index:])

    user_visual_str = "".join(user_visual)
    answer_visual_str = "".join(answer_visual)
    print(f"{e} | {answer_visual_str} | {user_visual_str} | {similarity:.2f}%")
    return is_correct


compare_answer("This is a incorrect answer", "is the correct answer 123")
