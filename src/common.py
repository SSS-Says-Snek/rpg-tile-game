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

TILE_WIDTH = 32
TILE_HEIGHT = 32
TILE_ROW = 30
TILE_COLUMN = 25

WIDTH = TILE_WIDTH * TILE_ROW
HEIGHT = TILE_HEIGHT * TILE_COLUMN
RES = (WIDTH, HEIGHT)

FPS = 60
BASE_FPS = 60

screen = pygame.Surface(RES)
pygame.display.set_mode(RES, pygame.DOUBLEBUF | pygame.OPENGL)

SOURCE_DIR = pathlib.Path("src")
ASSETS_DIR = pathlib.Path("assets")
SAVE_DIR = ASSETS_DIR / "save"
MAP_DIR = ASSETS_DIR / "maps"
FONT_DIR = ASSETS_DIR / "fonts"
IMG_DIR = ASSETS_DIR / "imgs"
SETTINGS_DIR = ASSETS_DIR / "settings"
ANIM_DIR = ASSETS_DIR / "imgs" / "animations"
SHADER_DIR = SOURCE_DIR / "display" / "shaders"
