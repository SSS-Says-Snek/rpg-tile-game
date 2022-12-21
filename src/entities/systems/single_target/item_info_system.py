"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame

from src.common import RES, screen
from src.display.transition import DarkenTransition, FadeTransition, EaseTransition
from src.display.widgets.button import DefaultButton
from src.entities.components import item_component
from src.entities.components.component import Position
from src.types import Entity

if TYPE_CHECKING:
    from src.states.level_state import LevelState

from src.entities.systems.system import System


class ItemInfoSystem(System):
    def __init__(self, level_state: LevelState):
        super().__init__(level_state)

        self.item: Optional[Entity] = None
        self.subscribe("player_get_item", self.on_player_get_item)

        self.screen = pygame.Surface(RES, pygame.SRCALPHA)

        duration = 500
        self.darken_game = DarkenTransition(
            mode=DarkenTransition.DARKEN,
            duration=duration,
            darken_threshold=0.8,
            ease_function=EaseTransition.ease_in_out_pow(1.5),
            finish_darken_callback=self.on_finish_darken_game,
            finish_lighten_callback=self.on_finish_lighten_game,
        )
        self.fade_self = FadeTransition(
            mode=FadeTransition.FADE_IN,
            duration=duration,
            ease_function=EaseTransition.ease_in_out_pow(1.5),
            screen=self.screen
        )

        self.ok_button = self.ui.add_widget(
            DefaultButton(
                self.ui,
                (600, 600),
                (100, 50),
                text="Okay",
                text_size=32,
                border_width=3,
                border_roundness=5,
                color=(100, 100, 100),
                hover_color=(80, 80, 80),
                fade_duration=700,
                click_callback=self.on_button_click,
                screen=self.screen,
            ),
            visible=False,
            manual_draw=True,
        )

    def on_finish_darken_game(self):
        """Activated when the game finished darkening"""

        self.level.pause()

    def on_finish_lighten_game(self):
        """Activated when the game finished lightening"""

        self.level.unpause()
        self.ui.toggle_visible(self.ok_button)

        item = self.world.component_for_entity(self.item, item_component.Item)
        owner_pos = self.world.component_for_entity(item.owner, Position)
        self.particle_manager.create_text_particle(owner_pos.pos, f"Acquired: {item.name}")

        self.item = None

    def on_player_get_item(self, item: Entity):
        """Activated when the player gets an item"""

        self.item = item

        self.darken_game.mode = DarkenTransition.DARKEN
        self.darken_game.start()

        self.fade_self.mode = FadeTransition.FADE_IN
        self.fade_self.start()

        self.ui.toggle_visible(self.ok_button)

    def on_button_click(self):
        """Activated when the okay button's clicked"""

        self.darken_game.mode = DarkenTransition.LIGHTEN
        self.darken_game.start()

        self.fade_self.mode = FadeTransition.FADE_OUT
        self.fade_self.start()

    def process(self):
        if self.item is not None:
            # Clears screen
            self.screen.fill(0)

            self.darken_game.draw()
            self.fade_self.draw()
            # Separately handles widget
            self.ui.handle_widget(self.ok_button)

            screen.blit(self.screen, (0, 0))
