import os
import random
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from glob import glob

import audio
from align_strings import align_strings

audio_dir = "./audios"
grade_dir = "./grade"
words_dir = "./words"

all_entry_chinese = []
lock = threading.Lock()


class Entry:
    def __init__(self, line: str):
        self.english = ""
        self.chinese = ""
        self.is_phrase = False
        self.audio_path = ""

        words = line.split(" ")
        for word in words:
            if word.isascii():
                self.english += word + " "
            else:
                self.chinese += word + " "

        self.english = self.english.strip(" \u3000")
        self.chinese = self.chinese.strip(" \u3000")
        self.is_phrase = self.english.count(" ") > 0
        self.audio_path = os.path.join(audio_dir, f"{self.english}.mp3")

    def __str__(self):
        return self.english + " " + self.chinese


def load_entries(file_name: str):
    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

        entries = []
        for line in lines:
            entry = Entry(line)
            if entry.english:
                entries.append(entry)

        return entries


def write_entries(file_name: str, entries: list):
    entries.sort(key=lambda entry: (entry.is_phrase, entry.english.lower()))

    max_english_length = 0
    for entry in entries:
        max_english_length = max(len(entry.english), max_english_length)
    max_english_length += 1

    with open(file_name, "w", encoding="utf-8") as file:
        for entry in entries:
            english_part = entry.english.ljust(max_english_length)
            chinese_part = entry.chinese
            file.write(f"{english_part} {chinese_part}\n\n")


def get_choice():
    user_input = input("Your choice: ").strip(" \u3000")

    if user_input.isdigit():
        user_choice = int(user_input)
        if 1 <= user_choice <= 4:
            return user_choice - 1
    else:
        user_input = user_input.upper()
        if user_input == "A":
            return 0
        elif user_input == "B":
            return 1
        elif user_input == "C":
            return 2
        elif user_input == "D":
            return 3

    print("Invalid choice.")
    return -1


def ask_chinese_meaning(entry: Entry):
    choices = [entry.chinese]
    k = 0
    while len(choices) < 4 and k < 10000:
        random_entry = random.choice(all_entry_chinese)
        k += 1
        if random_entry not in choices:
            choices.append(random_entry)

    random.shuffle(choices)
    choices[0], choices[2] = align_strings(choices[0], choices[2])

    print("🌐 Please choose the correct Chinese translation:")
    print("   A. " + choices[0] + "   B. " + choices[1])
    print("   C. " + choices[2] + "   D. " + choices[3])

    while True:
        user_choice = get_choice()
        if user_choice == -1:
            continue

        return choices[user_choice].strip(" \u3000") == entry.chinese


def get_answer(entry: Entry):
    print("> ", end="")
    audio.play(entry.audio_path)

    answer = input().strip(" \u3000")
    if answer == "":
        return ""

    answer_is_phrase = answer.count(" ") > 0
    if answer_is_phrase != entry.is_phrase:
        if entry.is_phrase:
            print("⚠️ This entry is phrase!")
        else:
            print("⚠️ This entry is a word!")
        return ""

    return answer


def dictation(entry: Entry):
    answer = ""
    while answer == "":
        answer = get_answer(entry)

    if answer.lower() != entry.english.lower():
        print(f"❌ Incorrect! {entry}")
        retry = ""
        while retry.strip(" \u3000").lower() != entry.english.lower():
            audio.play(entry.audio_path)
            retry = input("Try again: ")
        return False

    if not ask_chinese_meaning(entry):
        print(f"❌ Incorrect! {entry}")
        return False

    print(f"✅ Correct! {entry}")
    return True


def process_file(file: str):
    global all_entry_chinese, lock
    entries = load_entries(file)
    entry_chinese = []
    for entry in entries:
        entry_chinese.append(str(entry.chinese))
        audio.generate(entry.english, entry.audio_path)
    with lock:
        all_entry_chinese += entry_chinese
    write_entries(file, entries)


def get_dictation_file_path():
    files = glob(f"{words_dir}/*.md")
    with ThreadPoolExecutor(max_workers=64) as executor:
        executor.map(process_file, files)

    files.sort()
    print("\n📖 Dictation files:\n")
    for i, file in enumerate(files, 1):
        print(f" 💿 {i} {file[len(words_dir) + 1:-3]}")

    while True:
        user_choice = input("\n🎵 Please choose a dictation file id: ").strip(" \u3000")
        try:
            file_index = int(user_choice)
        except ValueError:
            continue
        if 0 < file_index <= len(files):
            print()
            return files[file_index - 1]


if __name__ == "__main__":
    os.makedirs(words_dir, exist_ok=True)
    os.makedirs(grade_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    audio.init(audio_dir)

    dictation_file_path = get_dictation_file_path()
    dictation_file_name = dictation_file_path[len(words_dir) + 1 : -3]

    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_file_name = f"{dictation_file_name}_{time}_grade.txt"
    result_file_path = os.path.join(grade_dir, result_file_name)

    print(f'\n🎧 Start dictation for "{dictation_file_name}".')

    entries = load_entries(dictation_file_path)
    random.shuffle(entries)

    word_number = len(entries)
    word_id = 0

    dictation_count = {}

    while True:
        wrong_entries = []

        for entry in entries:
            word_id += 1
            if entry.english.count(" ") == 0:
                print(f"\n📖 Word {word_id}/{word_number}:")
            else:
                print(f"\n📖 Phrase {word_id}/{word_number}:")

            entry_str = str(entry)
            if entry_str not in dictation_count:
                dictation_count[entry_str] = 1
            else:
                dictation_count[entry_str] += 1
            if not dictation(entry):
                wrong_entries.append(entry)
                word_number += 1

            with open(result_file_path, "w", encoding="utf-8") as file:
                for entry_str, count in dictation_count.items():
                    file.write(f"✅ {entry_str} (dictated {count} times)\n\n")

        if len(wrong_entries) == 0:
            print("Dictation finished! 🎉")
            subprocess.run(["open", grade_dir])
            sys.exit()

        entries = wrong_entries
