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
from src.types import Dts, Events

if TYPE_CHECKING:
    from src.states.level_state import LevelState


class System(esper.Processor):
    # For system-to-system interaction
    _send_to_graphics_widgets = []
    _listeners: dict[str, list[Callable]] = {}

    def __init__(self, level_state: "LevelState"):
        super().__init__()

        self.level: "LevelState" = level_state
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
        self._send_to_graphics_widgets.extend(zip(widgets, [when] * len(widgets)))

    def subscribe(self, event: str, func: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(func)

    def notify(self, event: str, *args, **kwargs):
        for func in self._listeners.get(event, []):
            func(*args, **kwargs)

    def process(self, event_list: Events, dts: Dts):
        pass
