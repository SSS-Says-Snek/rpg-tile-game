"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the Widget ABC
"""


from __future__ import annotations

from typing import Optional

from src.display.camera import Camera


class Widget:
    def __init__(self):
        """A base class for all game widgets"""

        self.interact_rect = None

    def draw(self, camera: Optional[Camera]):
        """
        Draws the widget

        Args:
            camera: The game camera
        """

        pass

    def update(self):
        """Updates the widget"""

        pass
