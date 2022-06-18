"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the Camera class, used to shift objects around
with respect to the player
"""

from typing import Union

from src import pygame

class Camera:
    def __init__(self, camera_width, camera_height):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera = pygame.Rect(0, 0, self.camera_width, self.camera_height)

    def apply(self, target_pos: Union[pygame.Rect, pygame.Vector2, tuple, list]):
        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)
        elif isinstance(target_pos, pygame.Vector2):
            target_pos = pygame.Rect(target_pos.x, target_pos.y, 0, 0)

        return target_pos.move(self.camera.topleft)

    def adjust_to(self, target_pos):
        x = self.camera_width // 2 - target_pos.x
        y = self.camera_height // 2 - target_pos.y
        self.camera.topleft = (x, y)
