"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import os
import pathlib
from functools import lru_cache
from typing import IO, Any, Callable, Iterable, Optional

from src import pygame
from src.common import ANIM_DIR, FONT_DIR
from src.display import animation
from src.types import Color
from src.utils.compat import removesuffix


class DirLoader:
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


@lru_cache(maxsize=256)
def load_img(path: pathlib.Path, mode: str = "alpha", colorkey: Optional[Color] = None) -> pygame.Surface:
    img = pygame.image.load(path)

    if mode == "alpha":
        img = img.convert_alpha()
    elif mode == "convert":
        img = img.convert()

    if colorkey is not None:
        img.set_colorkey(colorkey)

    return img


def load_img_dir(
    path: pathlib.Path, convert_mode: str = "alpha", colorkey: Optional[Color] = None
) -> list[pygame.Surface]:
    imgs = [pygame.image.load(file) for file in path.iterdir()]
    return load_imgs(imgs, convert_mode, colorkey)


def load_imgs(
    imgs: list[pygame.Surface], convert_mode: str = "alpha", colorkey: Optional[Color] = None
) -> list[pygame.Surface]:
    if convert_mode == "alpha":
        imgs = [img.convert_alpha() for img in imgs]
    elif convert_mode == "convert":
        imgs = [img.convert() for img in imgs]

    if colorkey is not None:
        for img in imgs:
            img.set_colorkey(colorkey)

    return imgs


@lru_cache(maxsize=512)
def load_font(size: int, font_name: str = "PixelMillenium"):
    return pygame.font.Font(FONT_DIR / f"{font_name}.ttf", size)


def load_mob_animations(mob_settings: dict, size: tuple[int, int] = (32, 32)):
    animations = {
        animation_type: animation.Animation(ANIM_DIR / mob_settings["animation_dir"] / f"{animation_type}.png", size)
        for animation_type in mob_settings["animation_types"]
    }

    return animations, mob_settings["animation_speed"]
