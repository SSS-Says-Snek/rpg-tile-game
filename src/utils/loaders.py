"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import os
import pathlib
from functools import lru_cache
from typing import IO, Callable, Generic, Iterable, Optional, TypeVar, Union, overload

from src import pygame
from src.common import ANIM_DIR, FONT_DIR
from src.display import animation
from src.types import Color, JSONSerializable, TupSize
from src.utils.compat import removesuffix

_T = TypeVar("_T")


class DirLoader(Generic[_T]):
    def __init__(
        self,
        data_dir: pathlib.Path,
        file_ext: str,
        data_loader: Callable[[IO], _T],
        open_mode: str = "r",
    ):
        """
        Loads an asset directory based on assets from the `data_loader` function

        Args:
            data_dir: The directory to load
            file_ext: The file extension of each asset
            data_loader: A function that converts a file handler to actual usable data
            open_mode: File open mode
        """

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

    @overload
    def __getitem__(self, items: tuple[str, ...]) -> list[_T]:
        ...

    @overload
    def __getitem__(self, items: str) -> _T:
        ...

    def __getitem__(self, items: Union[tuple[str, ...], str]) -> Union[list[_T], _T]:
        if not isinstance(items, tuple):
            split_keys = items.split("/")
            return self._reduce_dict(split_keys)
        else:
            split_keys = [item.split("/") for item in items]
            return [self._reduce_dict(split_key) for split_key in split_keys]

    def _reduce_dict(self, parts: Iterable[str]) -> Union[dict[str, _T], _T]:
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
def load_font(size: int, font_name: str = "PixelMillenium") -> pygame.font.Font:
    return pygame.font.Font(FONT_DIR / f"{font_name}.ttf", size)


def load_mob_animations(
    mob_settings: dict[str, JSONSerializable], size: TupSize = (32, 32)
) -> tuple[dict[str, animation.Animation], dict]:
    """
    Loads animations and animation speed given mob settings

    Args:
        mob_settings: Mob settings
        size: The size of the mob (frame)

    Returns:
        A dictionary of frames, as well as the playback speed of the animations
    """

    animations = {
        animation_type: animation.Animation(ANIM_DIR / mob_settings["animation_dir"] / f"{animation_type}.png", size)
        for animation_type in mob_settings["animation_types"]
    }

    return animations, mob_settings["animation_speed"]
