"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the base class of all systems
"""
from typing import TYPE_CHECKING

import esper

if TYPE_CHECKING:
    from src.states.level_state import LevelState


class System(esper.Processor):
    def __init__(self, level_state: "LevelState"):
        super().__init__()

        self.level_state: "LevelState" = level_state
        self.player = self.level_state.player

        self.camera = self.level_state.camera
        self.tilemap = self.level_state.tilemap
        self.particle_system = self.level_state.particle_system
        self.effect_system = self.level_state.effect_system

        self.world: esper.World = self.world

    def process(self, event_list, dts) -> None:
        pass
