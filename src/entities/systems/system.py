"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the base class of all systems
"""

import esper

class System(esper.Processor):
    def __init__(self, level_state):
        super().__init__()

        self.level_state = level_state
        self.player = self.level_state.player

    def process(self, event_list):
        # self.event_list = event_list
        pass
