from typing import Union

from src import pygame

class Camera:
    def __init__(self, camera_width, camera_height):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera = pygame.Rect(0, 0, self.camera_width, self.camera_height)

    def apply(self, target_rect: Union[pygame.Rect, tuple]):
        if isinstance(target_rect, tuple):
            target_rect = pygame.Rect(target_rect[0], target_rect[1], 0, 0)

        return target_rect.move(self.camera.topleft)

    def adjust_to(self, target_rect: pygame.Rect):
        x = self.camera_width // 2 - target_rect.x
        y = self.camera_height // 2 - target_rect.y
        self.camera.topleft = (x, y)
