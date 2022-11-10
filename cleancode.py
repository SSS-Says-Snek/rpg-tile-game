"""
A simple script to automate code cleanups.
Did not copy majority from PygameCommunityBot again
"""

from __future__ import annotations

import glob
import os
import pathlib
import subprocess
import sys

try:
    import black
except ImportError:
    print("We use black to format code. Please install it with 'pip install black'")
    raise SystemExit

try:
    import isort
except ImportError:
    print("We use isort to format code. Please install it with 'pip install isort'")
    raise SystemExit

HEADER_TEXT = '''"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
'''


class DummyPrinter:
    def success(self, msg):
        pass

    def error(self, msg):
        pass

    def diff_line(self, line):
        pass


def check_header_string():
    added_header = False
    for filepath in glob.iglob("**/*.py", recursive=True):
        file = pathlib.Path(os.getcwd(), filepath)
        file_data = file.read_text().lstrip()
        if file_data.startswith(HEADER_TEXT):
            continue

        if not file_data.startswith('"""'):
            added_header = True
            file.write_text(f'{HEADER_TEXT}"""\n\n{file_data}')
            print("Added header:", filepath)

    if not added_header:
        print("No files without headers!")


def check_imports():
    reorganized_imports = False
    isort.api.create_terminal_printer = lambda *args, **kwargs: DummyPrinter()

    for filepath in glob.iglob("**/*.py", recursive=True):
        file = pathlib.Path(os.getcwd(), filepath)
        if isort.file(file):
            reorganized_imports = True
            print("Reorganized import:", filepath)

    if not reorganized_imports:
        print("No imports in need of reorganizing!")


def cleanup_code():
    """
    Clean up all files of a given extension under a directory
    """
    for filepath in glob.iglob("**/*.py", recursive=True):
        path = pathlib.Path(os.getcwd(), filepath)
        if black.format_file_in_place(path, False, black.FileMode(line_length=119), black.WriteBack.YES):
            print("Formatted file:", filepath)
        else:
            print(f"Skipping file {filepath} as it is already formatted")

    print("\n====================== Adding headers ======================")
    check_header_string()

    print("\n====================== Reorganizing imports ======================")
    subprocess.run([sys.executable, "-m", "isort", "."])

    print("\n====================== Adding future imports ======================")
    subprocess.run(
        [sys.executable, "-m", "isort", ".", "--add-import", "from __future__ import annotations"],
        stdout=subprocess.DEVNULL,
    )
    print("Done!")

    # What is going on
    # print("\n====================== Reorganizing imports ======================")
    # check_imports()


if __name__ == "__main__":
    cleanup_code()
