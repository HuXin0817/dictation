rule = [",", "/", ";", "；", "。", " ", "\u3000"]


def fmt(w: str) -> str:
    for i in rule:
        w = w.replace(i, "，")

    return w
