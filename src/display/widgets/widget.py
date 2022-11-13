"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the Widget ABC
"""


from __future__ import annotations

from src.display.camera import Camera
from src.types import Dts, Events


class Widget:
    def __init__(self):
        self.interact_rect = None

    def draw(self, camera: Camera):
        pass

    def update(self, event_list: Events, dts: Dts):
        pass
