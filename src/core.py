"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains global state of various things for any file to access

Attributes:
    time (Time): A global state for the game's current time (adjusted with pausing)
"""

from __future__ import annotations

from src import pygame, common
from src.types import Events


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


class DT:
    def __init__(self, threshold_factor: float):
        """
        Contains various information regarding deltatime

        Args:
            threshold_factor: Factor of maximum adjusted DT (to compensate for SDL window pausing effect)
        """

        self.threshold_factor = threshold_factor
        self._dts = {"raw_dt": 0.0, "dt": 0.0}

    @property
    def dt(self) -> float:
        """
        Returns the adjusted deltatime

        Returns:
            Adjusted deltatime
        """

        return self._dts["dt"]

    @property
    def raw_dt(self) -> float:
        """
        Returns the raw deltatime

        Returns:
            Raw deltatime
        """

        return self._dts["raw_dt"]

    @dt.setter
    def dt(self, raw_dt: float):
        """
        Update both raw and adjusted dt based on raw dt

        Args:
            raw_dt: Raw deltatime
        """

        self._dts["raw_dt"] = min(raw_dt, self.threshold_factor / common.FPS)
        self._dts["dt"] = raw_dt * common.FPS

class Event:
    def __init__(self):
        self.events: Events = []

    def get(self):
        return self.events


# Glabal state, oooooo
time = Time()
event = Event()
dt = DT(1.5)

