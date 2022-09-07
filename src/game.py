"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the Game class, which contains vital data for states and is used to run the game
"""
from __future__ import annotations

import json

from src import common, pygame, screen

pygame.init()

from src.display.ui import UI
from src.states.level_state import LevelState
from src.states.state import State


class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # UI DRAWING MUST BE HANDLED IN THE STATE CODE DUE TO CONFLICTS FROM LEVEL_STATE
        self.ui = UI(None)

        with open(common.DATA_DIR / "settings.json") as f:
            self.settings: dict = json.load(f)

        self.state: State = LevelState(self)
        self.loaded_states: dict[type(State), State] = {LevelState: self.state}
        self.running: bool = True

        pygame.display.set_caption(self.settings["game"]["name"])

    def run(self):
        while self.running:
            # Set dt and events for other stuff to access via states
            events = pygame.event.get()
            dts = {"raw_dt": self.clock.tick(common.FPS) / 1000}
            dts["dt"] = dts["raw_dt"] * common.FPS

            pygame.display.set_caption(
                f"{self.settings['game']['name']} - {self.clock.get_fps():.3} FPS"
            )

            # Event loop
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # State handles event
                self.state.handle_event(event)

            # State runs other functions that get called once a frame
            self.state.update(events, dts)

            # State handles drawing
            self.state.draw()

            # State detector/switcher
            if self.state.next_state != self.state.__class__:
                old_state = self.state
                if self.state.next_state not in self.loaded_states:
                    self.loaded_states[self.state.next_state] = self.state.next_state(self)
                self.state = self.loaded_states[self.state.next_state]

                old_state.next_state = old_state.__class__  # Resets next state to self

            pygame.display.update()
        pygame.quit()
