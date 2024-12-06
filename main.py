import os
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from glob import glob

from contexttimer import Timer
from natsort import natsorted

import audio
from align_strings import align_strings
from answer_type import AnswerType
from cleaner import clear
from compare_answer import compare_answer

audio_dir = "./audios"
grade_dir = "./grade"
words_dir = "./words"

all_entry_chinese = []


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

    def judge(self, a: AnswerType) -> bool | None:
        if a == AnswerType.RIGHT:
            print(f"✅ Correct! {self}")
            return True
        elif a == AnswerType.WRONG:
            print(f"❌ Incorrect! {self}")
            return False

        return None


@lru_cache(maxsize=None)
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
    key = lambda entry: (entry.is_phrase, entry.english.lower())
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

    answer_exist = random.choice([True, False]) if choice_e else True
    if answer_exist:
        choices.append(entry.chinese)

    while len(choices) < 4:
        random_chinese = random.choice(all_entry_chinese)
        if random_chinese not in choices:
            choices.append(random_chinese)

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
        return entry.judge(chinese_meaning_answer_again)
    else:
        return entry.judge(chinese_meaning_answer)


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

    clear()
    print("\n🎧 Welcome to Dictation App!")
    print("📘 Practice your English dictation skills with phrases and words.")
    print("🔊 Make sure your audio is turned on for the best experience.\n")

    dictation_file_path = get_dictation_file_path()
    clear()

    dictation_file_name = ""
    entries = []
    if dictation_file_path == "REVIEW":
        files = glob(f"{words_dir}/*.md")
        for file in files:
            file_entries = load_entries(file)
            entries += file_entries
        dictation_file_name = "REVIEW"
        random.shuffle(entries)
        entries = entries[:30]
    else:
        dictation_file_name = dictation_file_path[len(words_dir) + 1 : -3]
        entries = load_entries(dictation_file_path)
        random.shuffle(entries)

    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_file_name = f"{dictation_file_name}_{time}_grade.txt"
    result_file_path = os.path.join(grade_dir, result_file_name)

    print(f'\n🎧 Start dictation for "{dictation_file_name}".')

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

            answer_is_right = dictation(entry)
            clear()

            if not answer_is_right:
                wrong_entries.append(entry)
                word_number += 1

            with open(result_file_path, "w", encoding="utf-8") as file:
                for entry_str, count in dictation_count.items():
                    file.write(f"✅ {entry_str} (dictated {count} times)\n\n")

        if len(wrong_entries) == 0:
            print("\nDictation finished! 🎉\n")
            subprocess.run(["open", grade_dir])
            break

        entries = wrong_entries
