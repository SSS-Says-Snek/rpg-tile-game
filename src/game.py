"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the Game class, which contains vital data for states and is used to run the game
"""

import json

from src import pygame, screen, common
from src.states.level_state import LevelState
from src.display.ui import UI

pygame.init()


class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.ui = UI(None)

        with open(common.DATA_DIR / "settings.json") as f:
            self.settings = json.load(f)

        self.state = LevelState(self)
        self.loaded_states = {LevelState: self.state}
        self.running = True
        self.dt = 0
        self.events = []

    def run(self) -> None:
        while self.running:
            # Set dt and events for other stuff to access via states
            self.dt = self.clock.tick(common.FPS) / 1000
            self.events = pygame.event.get()

            # Event loop
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False

                # State handles event
                self.state.handle_event(event)

            # State runs other functions that get called once a frame
            self.state.update()

            # State handles drawing
            self.state.draw()

            # UI drawing
            self.ui.draw()

            # State detector/switcher
            if self.state.next_state != self.state.__class__:
                old_state = self.state
                if self.state.next_state not in self.loaded_states:
                    self.loaded_states[self.state.next_state] = self.state.next_state(
                        self
                    )
                self.state = self.loaded_states[self.state.next_state]

                old_state.next_state = old_state.__class__  # Resets next state to self

            pygame.display.update()
        pygame.quit()
