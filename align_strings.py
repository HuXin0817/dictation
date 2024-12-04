import unicodedata


def count_fullwidth_and_halfwidth(input_string: str) -> (int, int):
    fullwidth_count = 0
    halfwidth_count = 0

    for char in input_string:
        if unicodedata.east_asian_width(char) in ["F", "W"]:  # 全角字符
            fullwidth_count += 1
        elif unicodedata.east_asian_width(char) == "H":  # 半角字符
            halfwidth_count += 1

    return fullwidth_count, halfwidth_count


def align_strings(string1: str, string2: str) -> (str, str):
    fullwidth_count1, halfwidth_count1 = count_fullwidth_and_halfwidth(string1)
    fullwidth_count2, halfwidth_count2 = count_fullwidth_and_halfwidth(string2)

    if fullwidth_count1 < fullwidth_count2:
        string1 += (fullwidth_count2 - fullwidth_count1) * "\u3000"
    else:
        string2 += (fullwidth_count1 - fullwidth_count2) * "\u3000"

    if halfwidth_count1 < halfwidth_count2:
        string1 += (halfwidth_count2 - halfwidth_count1) * " "
    else:
        string2 += (halfwidth_count1 - halfwidth_count2) * " "

    return string1, string2
