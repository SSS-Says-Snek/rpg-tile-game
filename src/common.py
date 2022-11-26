"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines some common variables
"""
from __future__ import annotations

import pathlib

import pygame

pygame.init()

TILE_WIDTH: int = 32
TILE_HEIGHT: int = 32
TILE_ROW: int = 30
TILE_COLUMN: int = 25

WIDTH: int = TILE_WIDTH * TILE_ROW
HEIGHT: int = TILE_HEIGHT * TILE_COLUMN
RES: tuple[int, int] = (WIDTH, HEIGHT)

FPS: int = 60
screen: pygame.Surface = pygame.Surface(RES).convert((255, 65280, 16711680, 0))
pygame.display.set_mode(RES, pygame.DOUBLEBUF | pygame.OPENGL)

SOURCE_DIR: pathlib.Path = pathlib.Path("src")
ASSETS_DIR: pathlib.Path = pathlib.Path("assets")
DATA_DIR: pathlib.Path = ASSETS_DIR / "data"
MAP_DIR: pathlib.Path = ASSETS_DIR / "maps"
FONT_DIR: pathlib.Path = ASSETS_DIR / "fonts"
IMG_DIR: pathlib.Path = ASSETS_DIR / "imgs"
SETTINGS_DIR: pathlib.Path = ASSETS_DIR / "settings"
ANIM_DIR: pathlib.Path = ASSETS_DIR / "imgs" / "animations"
SHADER_DIR: pathlib.Path = SOURCE_DIR / "display" / "shaders"
