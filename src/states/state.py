"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the State base class for all game states
"""

from __future__ import annotations

import abc
import importlib
from typing import TYPE_CHECKING

from src import pygame, screen
from src.types import Dts, Events

if TYPE_CHECKING:
    from src.game import Game


class State(abc.ABC):
    def __init__(self, game_class: "Game"):
        self.game_class = game_class
        self.next_state: type(State) = self.__class__
        self.screen = screen

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, event_list: Events, dts: Dts):
        pass

    def change_state(self, desired_state_str: str):
        state_module_name, state_name = desired_state_str.split(".")
        state_module = importlib.import_module(f"src.states.{state_module_name}")
        self.next_state = getattr(state_module, state_name)

        print(self.next_state)
