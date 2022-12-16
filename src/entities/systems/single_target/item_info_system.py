"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.display.transition import FadeTransition
from src.types import Entity

if TYPE_CHECKING:
    from src.states.level_state import LevelState

from src.entities.systems import System


class ItemInfoSystem(System):
    def __init__(self, level_state: LevelState):
        super().__init__(level_state)

        self.weapon_entity: Optional[Entity] = None
        self.subscribe("player_get_item", self.on_player_get_item)

        self.fade = FadeTransition(FadeTransition.FADE_OUT, 500, fade_out_frac=0.8)

    def on_player_get_item(self, weapon_entity: Entity):
        self.weapon_entity = weapon_entity
        self.fade.start()

    def process(self):
        if self.weapon_entity is not None:
            self.fade.draw()
