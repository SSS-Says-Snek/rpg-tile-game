"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.display.transition import FadeTransition
from src.display.widgets.button import DefaultButton
from src.types import Entity

if TYPE_CHECKING:
    from src.states.level_state import LevelState

from src.entities.systems.system import System


class ItemInfoSystem(System):
    def __init__(self, level_state: LevelState):
        super().__init__(level_state)

        self.weapon_entity: Optional[Entity] = None
        self.subscribe("player_get_item", self.on_player_get_item)

        self.fade = FadeTransition(
            FadeTransition.FADE_OUT,
            700,
            fade_out_frac=0.9,
            finish_out_callback=self.on_fade_out,
            finish_in_callback=self.on_fade_in,
        )

        self.ok_button = self.ui.add_widget(
            DefaultButton(
                self.ui,
                (100, 100),
                (100, 50),
                border_width=3,
                border_roundness=5,
                hover_color=(80, 80, 80),
                click_callback=self.on_button_click,
                fade_callback=self.on_button_fade
            ),
            visible=False,
            when="post_graphics_system",
        )

    def on_fade_out(self):
        self.ui.toggle_visible(self.ok_button)
        self.level.pause()

    def on_fade_in(self):
        self.level.unpause()

    def on_player_get_item(self, weapon_entity: Entity):
        self.weapon_entity = weapon_entity

        self.fade.mode = FadeTransition.FADE_OUT
        self.fade.start()

    def on_button_click(self):
        self.fade.mode = FadeTransition.FADE_IN
        self.fade.start()

    def on_button_fade(self):
        self.ui.toggle_visible(self.ok_button)

    def process(self):
        if self.weapon_entity is not None:
            self.fade.draw()
