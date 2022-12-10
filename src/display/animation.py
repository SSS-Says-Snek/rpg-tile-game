"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines some animation-related things
"""
from __future__ import annotations

import pathlib
from typing import Optional

from src import pygame, screen
from src.types import Size


class Animation:
    def __init__(
        self,
        spritesheet_path: Optional[pathlib.Path] = None,
        sprite_size: Optional[Size] = None,
        frames: Optional[list[pygame.Surface]] = None,
    ):
        """
        A class that makes it easy to handle animations

        Args:
            spritesheet_path: Path to directory of spritesheets
            sprite_size: Size of sprites
            frames: Number of frames
        """
        self.frames = frames if frames is not None else []

        if spritesheet_path is not None and sprite_size is not None and self.frames == []:
            self.frames = load_spritesheet(spritesheet_path, sprite_size)

        self.idx = 0
        self.num_frames = len(self.frames)

    def play_anim(self, blit_pos, raw_dt: float, play_speed: int):
        """
        Plays an animation and blits it on screen

        Args:
            blit_pos: The blitting position
            raw_dt: DT for independant framerates
            play_speed: The playing speed for the animation
        """

        self.idx += raw_dt * play_speed
        self.idx %= self.num_frames

        screen.blit(self.frames[int(self.idx)], blit_pos)


def load_spritesheet(spritesheet_path: pathlib.Path, sprite_size: Size) -> list[pygame.Surface]:
    images = []

    spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
    width, height = sprite_size

    num_rows = spritesheet.get_width() // width
    num_columns = spritesheet.get_height() // height

    for row in range(num_rows):
        for column in range(num_columns):
            image = spritesheet.subsurface(pygame.Rect(row * width, column * height, *sprite_size))
            images.append(image)

    return images
