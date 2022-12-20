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
        Provides an easy way to obtain numbers in a range from various easing functions.
        This does NOT have anything to do with the actual blitting of transitions.

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

    @staticmethod
    def ease_linear(x: float) -> float:
        return x

    def start(self):
        self.transitioning = True
        self.time_started = core.time.get_raw_ticks()

    def stop(self):
        self.transitioning = False
        self.value = self.default_end

    def update(self):
        if not self.transitioning:
            return

        time_elapsed = core.time.get_raw_ticks() - self.time_started
        self.value = self.ease_func(min(time_elapsed / self.duration, 1)) * self.range + self.begin

        if core.time.get_raw_ticks() - self.time_started > self.duration:
            self.transitioning = False
            self.value = self.default_end
            if self.callback is not None:
                self.callback()


class DarkenTransition:
    DARKEN = 0
    LIGHTEN = 1

    def __init__(
        self,
        mode: int,
        duration: int,
        darken_threshold: float = 1,
        ease_function: Callable[[float], float] = EaseTransition.ease_linear,
        finish_darken_callback: Optional[VoidFunc] = None,
        finish_lighten_callback: Optional[VoidFunc] = None,
        screen: pygame.Surface = screen,
    ):
        """
        Provides an easy way to darken a desired surface with linear interpolation

        Args:
            mode: Mode to fade
            duration: How long, in milliseconds, the transition should last
            darken_threshold: At what level it should stop getting darker
            screen: What surface to fade. Defaults to `screen`
        """

        self.mode = mode
        self.duration = duration
        self.screen = screen

        self.alpha = 255 if mode == self.LIGHTEN else 0
        self.fade_out = darken_threshold * 255
        self.ease_function = ease_function

        self.time_started = 0
        self.transitioning = False
        self.finish_out_callback = finish_darken_callback
        self.finish_in_callback = finish_lighten_callback

        self.darken = pygame.Surface(screen.get_size())
        self.darken.set_alpha(self.alpha)

    def start(self):
        """Starts a transition"""

        self.transitioning = True
        self.time_started = core.time.get_raw_ticks()

    def update(self):
        if self.transitioning:
            time_elapsed = core.time.get_raw_ticks() - self.time_started
            duration_frac = time_elapsed / self.duration
            eased_frac = self.ease_function(duration_frac)

            if self.mode == self.LIGHTEN:
                self.alpha = self.fade_out - (eased_frac * 255)
            else:
                self.alpha = eased_frac * self.fade_out

            if duration_frac > 1:
                if self.finish_out_callback is not None and self.mode == self.DARKEN:
                    self.finish_out_callback()
                elif self.finish_in_callback is not None and self.mode == self.LIGHTEN:
                    self.finish_in_callback()

                self.transitioning = False
                # Just in case it overreached
                if self.mode == self.DARKEN:
                    self.alpha = self.fade_out
                else:
                    self.alpha = 0

            self.darken.set_alpha(self.alpha)

    def draw(self):
        """Draws (and updates) darkening"""

        self.update()
        self.screen.blit(self.darken, (0, 0))


class FadeTransition(DarkenTransition):
    FADE_IN = 0
    FADE_OUT = 1

    DARKEN = FADE_IN
    LIGHTEN = FADE_OUT

    def draw(self):
        # Basically everything is reversed because of some naming discrepancies for DarkenTransition
        self.update()
        
        if self.transitioning:
            self.screen.set_alpha(self.alpha)
