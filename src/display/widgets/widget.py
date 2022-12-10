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
        """A base class for all game widgets"""

        self.interact_rect = None

    def draw(self, camera: Camera):
        """
        Draws the widget

        Args:
            camera: The game camera
        """

        pass

    def update(self, event_list: Events, dts: Dts):
        """
        Updates the widget

        Args:
            event_list: List of events that happened this frame
            dts: Delta time of this event
        """

        pass
