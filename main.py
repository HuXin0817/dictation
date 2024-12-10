import random
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from glob import glob

from clear_screen import clear
from contexttimer import Timer
from natsort import natsorted

import audio
from align_strings import align_strings
from cache import cache
from compare_answer import compare_answer
from config import *
from entry import Entry
from semantic_similarity import load_embedding, semantic_similarity

info = """
🎧 Welcome to Dictation App!"
📘 Practice your English dictation skills with phrases and words.
🔊 Make sure your audio is turned on for the best experience.
"""

if not clear_is_valid:
    clear = lambda: None


all_entry_chinese = []


class AnswerType(Enum):
    RIGHT = 0
    WRONG = 1
    NOT_EXIST = 2


@cache
def load_entries(file_name: str) -> list[Entry]:
    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

        entries = []
        for line in lines:
            entry = Entry(line)
            if entry.english:
                entries.append(entry)

        return entries


def write_entries(file_name: str, entries: list[Entry]) -> None:
    key = lambda entry: (entry.is_phrase, entry.lower_english)
    entries.sort(key=key)

    max_english_length = 0
    for entry in entries:
        max_english_length = max(len(entry.english), max_english_length)
    max_english_length += 1

    with open(file_name, "w", encoding="utf-8") as file:
        for entry in entries:
            english_part = entry.english.ljust(max_english_length)
            chinese_part = entry.chinese
            file.write(f"{english_part} {chinese_part}\n\n")


def get_choice(choice_number: int) -> int | None:
    assert choice_number == 4 or choice_number == 5

    user_input = input("Your choice: ").strip(" \u3000")

    if user_input.isdigit():
        user_choice = int(user_input)
        if 1 <= user_choice <= choice_number:
            return user_choice
    else:
        user_input = user_input.upper()
        if user_input == "A":
            return 1
        elif user_input == "B":
            return 2
        elif user_input == "C":
            return 3
        elif user_input == "D":
            return 4
        elif user_input == "E" and choice_number == 5:
            return 5

    audio.beep()
    return None


def ask_chinese_meaning(entry: Entry, choice_e: bool) -> AnswerType:
    choices = []

    answer_exist = random.choice([True, True, False]) if choice_e else True
    if answer_exist:
        choices.append(entry.chinese)

    k = 0
    while len(choices) < 4 and k < 10000:
        k += 1
        random_chinese = random.choice(all_entry_chinese)
        if random_chinese == entry.chinese:
            continue
        if random_chinese in choices:
            continue
        similarity = semantic_similarity(random_chinese, entry.chinese)
        if similarity < 0.9:
            choices.append(random_chinese)

    while len(choices) < 4:
        choices.append("")

    random.shuffle(choices)
    choices[0], choices[2] = align_strings(choices[0], choices[2])

    print(f'🌐 Word "{entry.english}" Chinese translation:')
    print("   A. " + choices[0] + "   B. " + choices[1])
    print("   C. " + choices[2] + "   D. " + choices[3])
    if choice_e:
        print("   E. answer not exist.")

    right_answer = 5
    for i in range(4):
        if choices[i].strip(" \u3000") == entry.chinese:
            right_answer = i + 1

    while True:
        user_choice = get_choice(5 if choice_e else 4)
        if user_choice is None:
            continue

        if user_choice == right_answer:
            if user_choice == 5:
                return AnswerType.NOT_EXIST
            else:
                return AnswerType.RIGHT
        else:
            return AnswerType.WRONG


def get_answer(entry: Entry) -> str | None:
    print("> ", end="")
    audio.play(entry.audio_path)

    answer = input().strip(" \u3000")
    if answer == "":
        audio.beep()
        return None

    answer_is_phrase = answer.count(" ") > 0
    if answer_is_phrase != entry.is_phrase:
        if entry.is_phrase:
            print("⚠️ This entry is phrase!")
        else:
            print("⚠️ This entry is a word!")
        audio.beep()
        return None

    return answer


def dictation(entry: Entry) -> bool:
    user_answer = None
    while user_answer is None:
        user_answer = get_answer(entry)

    if not compare_answer(user_answer, entry.english):
        while True:
            audio.play(entry.audio_path)
            retry = input("Try again: ").strip(" \u3000")
            if retry != "":
                if compare_answer(retry, entry.english):
                    return False

    chinese_meaning_answer = ask_chinese_meaning(entry, choice_e=True)
    if chinese_meaning_answer == AnswerType.NOT_EXIST:
        chinese_meaning_answer_again = ask_chinese_meaning(entry, choice_e=False)
        return chinese_meaning_answer_again == AnswerType.RIGHT
    else:
        return chinese_meaning_answer == AnswerType.RIGHT


def load_all_chinese_embedding():
    split_words = []
    for w in all_entry_chinese:
        split_words.append(w.split("，"))
    with ThreadPoolExecutor(max_workers=32) as executor:
        executor.map(load_embedding, split_words)


def get_dictation_file_path() -> str:
    files = natsorted(glob(f"{words_dir}/*.md"))
    file_entry_count = []

    global all_entry_chinese
    for file in files:
        file_entries = load_entries(file)
        for entry in file_entries:
            all_entry_chinese.append(entry.chinese)
        write_entries(file, file_entries)
        file_entry_count.append(len(file_entries))
    all_entry_chinese = list(set(all_entry_chinese))
    assert len(all_entry_chinese) >= 4
    threading.Thread(target=load_all_chinese_embedding).start()

    print("💿 Start generating audios...")
    with Timer() as timer:
        process_entry = lambda entry: audio.generate(entry.english, entry.audio_path)

        while True:
            no_audio_entries = []

            for file in files:
                for entry in load_entries(file):
                    if not os.path.exists(entry.audio_path):
                        no_audio_entries.append(entry)

            if len(no_audio_entries) == 0 and audio.delete_invalid_mp3(audio_dir) == 0:
                break

            with ThreadPoolExecutor(max_workers=32) as executor:
                executor.map(process_entry, no_audio_entries)

    print(f"✨ Audio generation completed in {timer.elapsed:.2f} seconds.\n")
    print("📖 Dictation files:\n")

    max_length = max(len(file) for file in files) - len(words_dir) - 4
    max_num_length = len(str(len(files) + 1))

    for i, file in enumerate(files, 1):
        number = str(i).rjust(max_num_length)
        file_name = file[len(words_dir) + 1 : -3].ljust(max_length)
        words_number = file_entry_count[i - 1]
        print(f" 💿 {number} {file_name}  ({words_number} Words)")

    print(f" 💿 {str(len(files) + 1).rjust(max_num_length)} REVIEW\n")

    while True:
        user_choice = input("🎵 Please choose a dictation file id: ").strip(" \u3000")
        try:
            file_index = int(user_choice)
        except ValueError:
            audio.beep()
            continue
        if 0 < file_index <= len(files):
            return files[file_index - 1]
        elif file_index == len(files) + 1:
            return "REVIEW"
        else:
            audio.beep()


if __name__ == "__main__":
    os.makedirs(words_dir, exist_ok=True)
    os.makedirs(grade_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    print(info)

    dictation_file_path = get_dictation_file_path()

    dictation_file_name = ""
    entries = []
    if dictation_file_path == "REVIEW":
        files = glob(f"{words_dir}/*.md")
        for file in files:
            file_entries = load_entries(file)
            entries += file_entries
        dictation_file_name = "REVIEW"
        random.shuffle(entries)
        entries = entries[:10]
    else:
        dictation_file_name = dictation_file_path[len(words_dir) + 1 : -3]
        entries = load_entries(dictation_file_path)
        random.shuffle(entries)

    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_file_name = f"{dictation_file_name}_{time}_grade.txt"
    result_file_path = os.path.join(grade_dir, result_file_name)

    clear()
    print(f'\n🎧 Start dictation for "{dictation_file_name}".')

    word_number = len(entries)
    word_id = 0

    dictation_count = {}

    while True:
        wrong_entries = []

        for entry in entries:
            word_id += 1
            if entry.is_phrase:
                print(f"\n📖 Phrase {word_id}/{word_number}:")
            else:
                print(f"\n📖 Word {word_id}/{word_number}:")

            entry_str = str(entry)
            if entry_str not in dictation_count:
                dictation_count[entry_str] = 1
            else:
                dictation_count[entry_str] += 1

            answer_is_right = dictation(entry)

            if not answer_is_right:
                wrong_entries.append(entry)
                word_number += 1

            with open(result_file_path, "w", encoding="utf-8") as file:
                for entry_str, count in dictation_count.items():
                    file.write(f"✅ {entry_str} (dictated {count} times)\n\n")

            print(f"📖 {entry}")
            if not answer_is_right:
                input("type a word to continue.")
            clear()

        if len(wrong_entries) == 0:
            print("\nDictation finished! 🎉")
            clear()
            subprocess.run(["open", grade_dir])
            break

        entries = wrong_entries
