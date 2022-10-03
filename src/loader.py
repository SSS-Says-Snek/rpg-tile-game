"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import os
import pathlib
from typing import Callable, Iterable, Any, IO

from src.utils import removesuffix


class Loader:
    def __init__(
        self,
        data_dir: pathlib.Path,
        file_ext: str,
        data_loader: Callable[[IO], Any],
        open_mode: str = "r",
    ):
        self.data = {}

        for directory, subcategories, setting_filenames in os.walk(data_dir):
            for subcategory in subcategories:
                subcategory_path = pathlib.Path(os.path.join(directory, subcategory))
                parts = subcategory_path.relative_to(data_dir).parts[:-1]

                current_dict = self._reduce_dict(parts)
                current_dict[subcategory] = {}

            for setting_filename in setting_filenames:
                setting_file_path = pathlib.Path(os.path.join(directory, setting_filename))
                with open(setting_file_path, open_mode) as f:
                    parts = setting_file_path.relative_to(data_dir).parts[:-1]
                    key = removesuffix(setting_filename, file_ext)

                    current_dict = self._reduce_dict(parts)
                    current_dict[key] = data_loader(f)

    def __getitem__(self, items):
        if not isinstance(items, tuple):
            split_keys = items.split("/")
            return self._reduce_dict(split_keys)
        else:
            split_keys = [item.split("/") for item in items]
            return [self._reduce_dict(split_key) for split_key in split_keys]

    def _reduce_dict(self, parts: Iterable[str]) -> dict:
        """Utilizes dict references to grab a portion of settings to be updated"""

        current_dict = self.data
        for part in parts:
            current_dict = current_dict[part]
        return current_dict
