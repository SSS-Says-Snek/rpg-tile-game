"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the base class of all systems
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import esper

from src.display.widgets.widget import Widget

if TYPE_CHECKING:
    from src.states.level_state import LevelState


class System(esper.Processor):
    # For system-to-system interaction
    _send_to_graphics_widgets: list[tuple[Widget, str]] = []
    _listeners: dict[str, list[Callable]] = {}

    def __init__(self, level_state: LevelState):
        """
        A base class for all ECS systems (E.g graphics system, collision system)

        Args:
            level_state: The level state
        """

        super().__init__()

        self.level: LevelState = level_state
        self.player = self.level.player

        self.settings = self.level.settings
        self.imgs = self.level.imgs
        self.camera = self.level.camera
        self.tilemap = self.level.tilemap
        self.particle_system = self.level.particle_system
        self.effect_system = self.level.effect_system

        self.world: esper.World = self.world
        self.ui = self.level.ui

    def send_to_graphics(self, *widgets: Widget, when: str = "post_ui"):
        """
        Sends multiple widgets to the graphics system to be processed

        Args:
            *widgets: Widgets to send to the graphics system
            when: A string indicating when it should be processed (goofy version of z index)
        """

        self._send_to_graphics_widgets.extend(zip(widgets, [when] * len(widgets)))

    def subscribe(self, event: str, func: Callable):
        """
        Allows the system to subscribe to any event

        Args:
            event: The event name
            func: A function that will get called when event is triggered
        """

        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(func)

    def notify(self, event: str, *args, **kwargs):
        """
        Notifies all systems of the event happening

        Args:
            event: The event name
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """

        for func in self._listeners.get(event, []):
            func(*args, **kwargs)

    def process(self):
        """Processes stuff (sorry that's the best I got :( )"""

        pass
