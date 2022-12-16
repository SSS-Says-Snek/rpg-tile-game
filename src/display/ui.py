"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the UI class, used to handle... the game UI
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import esper

from src.display.camera import Camera
from src.display.particle import ParticleManager
from src.display.widgets.widget import Widget


@dataclass
class WidgetInfo:
    widget: Widget
    visible: bool
    when: str

    def __iter__(self) -> Iterable:
        yield self.widget
        yield self.visible
        yield self.when


class UI:
    def __init__(self, camera: Optional[Camera] = None):
        """
        A user interface manager for the entire game

        Args:
            camera: The game camera
        """

        self.current_uuid = 0

        self.camera = camera
        self.world: Optional[esper.World] = None
        self.particle_manager: Optional[ParticleManager] = None

        self.widgets: dict[int, WidgetInfo] = {}
        self.hud_widgets: dict[str, WidgetInfo] = {}

    def draw(self):
        """Draws all widgets"""

        for widget, visible, when in self.widgets.copy().values():
            if not visible or when != "graphics_system":
                continue

            widget.draw(self.camera)

    def draw_post_graphics_system(self):
        for widget, visible, when in self.widgets.copy().values():
            if not visible or when != "post_graphics_system":
                continue

            widget.draw(self.camera)

    def update(self):
        """Updates all widgets in the user interface"""

        for widget, visible, _ in self.widgets.values():
            if not visible:
                continue

            widget.update()

    def add_widget(self, widget: Widget, visible: bool = True, when: str = "graphics_system") -> int:
        """
        Adds a widget to the UI

        Args:
            widget: The widget to add
            visible: Whether it is currently visible or not
            when: When to render the widget

        Returns:
            An ID for the widget
        """

        widget.uuid = self.current_uuid
        self.widgets[self.current_uuid] = WidgetInfo(widget, visible, when)

        self.current_uuid += 1
        return widget.uuid

    def add_hud_widget(self, widget, hud_name: str, visible: bool = True, when: str = "graphics_system"):
        """
        Adds an HUD widget to the UI

        Args:
            widget: The HUD widget to add
            hud_name: The HUD name to reference it elsewhere
            visible: Whether it is currently visible or not
            when: When to render the widget

        Returns:
            An ID for the widget
        """
        self.hud_widgets[hud_name] = WidgetInfo(widget, visible, when)
        self.add_widget(widget, visible)

    def remove_widget(self, uuid: int):
        """
        Remove a widget given ID

        Args:
            uuid: ID of widget
        """

        del self.widgets[uuid]

    def toggle_visible(self, uuid: int):
        """
        Toggles visibility of widget

        Args:
            uuid: ID of widget
        """

        self.widgets[uuid].visible = not self.widgets[uuid].visible
