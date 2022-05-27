import pygame
import pathlib

TILE_WIDTH = 16
TILE_HEIGHT = 16
TILE_ROW = 50
TILE_COLUMN = 50

WIDTH = TILE_WIDTH * TILE_ROW
HEIGHT = TILE_HEIGHT * TILE_COLUMN
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))

ASSETS_DIR = pathlib.Path("assets")
MAP_DIR = ASSETS_DIR / "maps"
