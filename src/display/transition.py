"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains utilities to transition from one value to another.
The transition values can then be used in a variety of things (position, opacity, etc.)
"""
from __future__ import annotations

from typing import Callable, Optional

from src import core, pygame, screen
from src.types import VoidFunc


class FadeTransition:
    FADE_IN = 0
    FADE_OUT = 1
    FADE_OUT_IN = 2

    def __init__(self, mode: int, duration: int, fade_out_frac: float = 1, finish_out_callback: Optional[VoidFunc] = None, surf: pygame.Surface = screen):
        """
        Provides an easy way to darken a desired surface with linear interpolation

        Args:
            mode: Mode to fade
            duration: How long, in milliseconds, the transition should last
            fade_out_frac: At what level it should stop getting darker
            surf: What surface to fade. Defaults to `screen`
        """

        self.mode = mode
        self.duration = duration
        self.screen_to_fade = surf

        self.alpha = 255 if mode == self.FADE_IN else 0
        self.fade_out = fade_out_frac * 255

        self.time_started = 0
        self.transitioning = False
        self.finish_out_callback = finish_out_callback

        self.darkness = pygame.Surface(surf.get_size())
        self.darkness.set_alpha(self.alpha)

    def start(self):
        """Starts a transition"""

        self.transitioning = True
        self.time_started = core.time.get_raw_ticks()

    def draw(self):
        """Draws (and updates) darkening"""

        if self.transitioning:
            time_elapsed = core.time.get_raw_ticks() - self.time_started
            duration_frac = time_elapsed / self.duration

            if self.mode == self.FADE_IN:
                self.alpha = 255 - (duration_frac * 255)
            else:
                self.alpha = duration_frac * self.fade_out

            if duration_frac > 1:
                if self.finish_out_callback is not None and self.mode == self.FADE_OUT:
                    self.finish_out_callback()

                self.transitioning = False
                # Just in case it overreached
                if self.mode == self.FADE_OUT:
                    self.alpha = self.fade_out
                else:
                    self.alpha = 0

            self.darkness.set_alpha(self.alpha)
        self.screen_to_fade.blit(self.darkness, (0, 0))


class EaseTransition:
    def __init__(
        self,
        begin: float,
        end: float,
        duration: int,
        ease_func: Callable[[float], float],
        default_end: Optional[float] = None,
        callback: Optional[VoidFunc] = None,
    ):
        """
        Provides an easy way to obtain numbers in a range from various easing functions

        Args:
            begin: The beginning
            end: The end
            duration: The duration
            ease_func: The easing function
            default_end: What the value will default to after each transition
            callback: A function that is called when each transition is finished
        """

        self.begin = begin
        self.end = end
        self.range = end - begin
        self.duration = duration
        self.ease_func = ease_func
        self.default_end = default_end
        self.callback = callback

        self.transitioning = False
        self.time_started = 0
        self.value = None

    @staticmethod
    def ease_in_out_quad(x: float) -> float:
        if x < 0.5:
            return 2 * x**2
        return 1 - (-x * 2 + 2) ** 2 / 2

    @staticmethod
    def ease_out_quad(x: float) -> float:
        return 1 - (1 - x) ** 2

    @staticmethod
    def ease_out_cub(x: float) -> float:
        return 1 - (1 - x) ** 3

    @staticmethod
    def ease_out_pow(power: int) -> Callable[[float], float]:
        def inner(x: float):
            return 1 - (1 - x) ** power

        return inner

    @staticmethod
    def ease_out_exp(x: float) -> float:
        if x == 1:
            return 1
        return 1 - (2 ** (-10 * x))

    def start(self):
        self.transitioning = True
        self.time_started = core.time.get_ticks()

    def stop(self):
        self.transitioning = False
        self.value = self.default_end

    def update(self):
        if not self.transitioning:
            return

        time_elapsed = core.time.get_ticks() - self.time_started
        self.value = self.ease_func(min(time_elapsed / self.duration, 1)) * self.range + self.begin

        if core.time.get_ticks() - self.time_started > self.duration:
            self.transitioning = False
            self.value = self.default_end
            if self.callback is not None:
                self.callback()
