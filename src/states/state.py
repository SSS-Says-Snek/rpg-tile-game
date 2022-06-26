"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the State base class for all game states
"""

import importlib
import abc

from src import pygame, screen


class State(abc.ABC):
    def __init__(self, game_class):
        self.game_class = game_class
        self.next_state = self.__class__
        self.screen = screen

    @abc.abstractmethod
    def draw(self) -> None:
        pass

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self) -> None:
        pass

    def change_state(self, desired_state_str: str):
        state_module_name, state_name = desired_state_str.split(".")
        state_module = importlib.import_module(f"src.states.{state_module_name}")
        self.next_state = getattr(state_module, state_name)

        print(self.next_state)
