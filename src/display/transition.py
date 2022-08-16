"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from src import pygame, screen


class FadeTransition:
    FADE_IN = 0
    FADE_OUT = 1

    def __init__(self, mode, fade_rate, screen_to_fade=screen):
        self.mode = mode
        self.fade_rate = fade_rate
        self.screen_to_fade = screen_to_fade

        self.alpha = 255 if mode == self.FADE_IN else 0
        self.darkness = pygame.Surface(screen_to_fade.get_size())
        self.darkness.set_alpha(self.alpha)

    def draw(self):
        if self.mode == self.FADE_IN:
            self.alpha = max(self.alpha - self.fade_rate, 0)
        else:
            self.alpha = min(self.alpha + self.fade_rate, 255)

        self.darkness.set_alpha(self.alpha)
        self.screen_to_fade.blit(self.darkness, (0, 0))
