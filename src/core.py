"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

Attributes:
    time (Time): A global state for the game's current time (adjusted with pausing)
"""

from __future__ import annotations

from src import pygame


class Time:
    def __init__(self):
        """Class used to manage time (specifically handles pauses). Drop-in replacement for pygame.time.get_ticks()"""

        self.offsetted_time = 0

        self.pause_time = 0
        self.paused = False

    def get_ticks(self):
        """
        Gets ticks since pygame app was opened, adjusted with pausing

        Returns:
            float: Ticks since pygame app opened, adjusted with pausing
        """

        if not self.paused:
            return pygame.time.get_ticks() - self.offsetted_time
        return self.pause_time

    def pause(self):
        """Pauses time. Any call to `get_ticks` will return the paused time"""

        if not self.paused:
            self.pause_time = pygame.time.get_ticks() - self.offsetted_time
            self.paused = True

    def unpause(self):
        """Unpauses time. Offset time is set to adjust for pause duration, `get_ticks` behaves normally"""

        if self.paused:
            self.offsetted_time = pygame.time.get_ticks() - self.pause_time
            self.paused = False


# Glabal state, oooooo
time = Time()
