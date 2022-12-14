"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the Game class, which contains vital data for states and is used to run the game
"""
from __future__ import annotations

import json

from src import common, core, pygame
from src.common import IMG_DIR, SETTINGS_DIR
from src.display.shaders import ShaderManager
from src.types import JSONSerializable
# from src.display.widgets.button import DefaultButton
from src.utils.loaders import DirLoader

pygame.init()

from src.display.ui import UI
from src.states.level_state import LevelState
from src.states.state import State


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()

        # UI DRAWING MUST BE HANDLED IN THE STATE CODE DUE TO CONFLICTS FROM LEVEL_STATE
        # No camera at start of game
        self.ui = UI()

        # Shader manager to handle shaders and actually draw proxy screen onto actual screen
        self.shader_manager = ShaderManager()

        # self.ui.add_widget(
        #     DefaultButton(
        #         self.ui,
        #         (100, 100),
        #         (100, 50),
        #         border_width=3,
        #         border_roundness=5,
        #         hover_color=(80, 80, 80),
        #     )
        # )

        # Loaders
        self.settings: DirLoader[JSONSerializable] = DirLoader(SETTINGS_DIR, ".json", json.load)
        self.imgs: DirLoader[pygame.Surface] = DirLoader(IMG_DIR, ".png", pygame.image.load)

        # States
        self.state: State = LevelState(self)
        self.loaded_states: dict[type[State], State] = {LevelState: self.state}
        self.running = True

        # Set caption
        self.game_name = self.settings["game/name"]
        pygame.display.set_caption(self.game_name)

    def run(self):
        while self.running:
            # Set dt and events for other stuff to access via states
            events = pygame.event.get()
            core.event.events = events
            core.dt.dt = self.clock.tick(common.FPS) / 1000

            pygame.display.set_caption(f"{self.game_name} - {self.clock.get_fps():.3f} FPS")

            # Event loop
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # State handles event
                self.state.handle_event(event)

            # State runs other functions that get called once a frame
            self.state.update()

            # State handles drawing
            self.state.draw()

            # Renders screen
            self.shader_manager.render()

            # State detector/switcher
            if self.state.next_state != type(self.state):
                old_state = self.state
                if self.state.next_state not in self.loaded_states:
                    # Instantiate new state
                    self.loaded_states[self.state.next_state] = self.state.next_state(self)
                self.state = self.loaded_states[self.state.next_state]

                old_state.next_state = type(old_state)  # Resets next state to self

        pygame.quit()
