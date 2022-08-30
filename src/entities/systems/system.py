"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the base class of all systems
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import esper

if TYPE_CHECKING:
    from src.states.level_state import LevelState


class System(esper.Processor):
    _send_to_graphics_widgets = []

    def __init__(self, level_state: "LevelState"):
        super().__init__()

        self.level_state: "LevelState" = level_state
        self.player = self.level_state.player

        self.camera = self.level_state.camera
        self.tilemap = self.level_state.tilemap
        self.particle_system = self.level_state.particle_system
        self.effect_system = self.level_state.effect_system

        self.world: esper.World = self.world

    def send_to_graphics(self, *widgets):
        self._send_to_graphics_widgets.extend(widgets)

    def process(self, event_list, dts) -> None:
        pass
