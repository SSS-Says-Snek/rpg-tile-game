from typing import Union

from src import pygame

class Camera:
    def __init__(self, camera_width, camera_height):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera = pygame.Rect(0, 0, self.camera_width, self.camera_height)

    def apply(self, target_pos: Union[pygame.Rect, tuple, list]):
        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)

        return target_pos.move(self.camera.topleft)

    def adjust_to(self, target_pos):
        x = self.camera_width // 2 - target_pos[0]
        y = self.camera_height // 2 - target_pos[1]
        self.camera.topleft = (x, y)
