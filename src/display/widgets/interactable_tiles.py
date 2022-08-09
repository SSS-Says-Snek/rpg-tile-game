import math

from src import pygame, screen


class InteractableTileHover:
    def __init__(self, tile):
        self.x = tile.x
        self.y = tile.y - 2

        self.rect = pygame.Rect(self.x * tile.tile_width, self.y * tile.tile_height, tile.tile_width, tile.tile_height)

    def draw(self, camera):
        rect_copy = self.rect.copy()
        rect_copy.y += round(math.sin(pygame.time.get_ticks() / 150) * 5)

        pygame.draw.rect(screen, (255, 0, 0), camera.apply(rect_copy))
