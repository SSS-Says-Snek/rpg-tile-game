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
    manual_draw: bool

    def __iter__(self) -> Iterable:
        yield self.widget
        yield self.visible
        yield self.manual_draw


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

        for widget, visible, manual_draw in self.widgets.copy().values():
            if not visible or manual_draw:
                continue

            widget.draw(self.camera)

    def update(self):
        """Updates all widgets in the user interface"""

        for widget, visible, manual_draw in self.widgets.values():
            if not visible or manual_draw:
                continue

            widget.update()

    def add_widget(self, widget: Widget, visible: bool = True, manual_draw: bool = False) -> int:
        """
        Adds a widget to the UI

        Args:
            widget: The widget to add
            visible: Whether it is currently visible or not
            manual_draw: Whether to let the user handle it with `handle_widget` or not

        Returns:
            An ID for the widget
        """

        widget.uuid = self.current_uuid
        self.widgets[self.current_uuid] = WidgetInfo(widget, visible, manual_draw)

        self.current_uuid += 1
        return widget.uuid

    def add_hud_widget(self, widget, hud_name: str, visible: bool = True, manual_draw: bool = False):
        """
        Adds an HUD widget to the UI

        Args:
            widget: The HUD widget to add
            hud_name: The HUD name to reference it elsewhere
            visible: Whether it is currently visible or not
            manual_draw: Whether to let the user handle it with `handle_widget` or not

        Returns:
            An ID for the widget
        """
        self.hud_widgets[hud_name] = WidgetInfo(widget, visible, manual_draw)
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

    def handle_widget(self, uuid: int):
        """
        Handles widget directly
        TODO: Find a better way than this heheheha

        Args:
            uuid: ID of widget
        """

        widget = self.widgets[uuid]

        if widget.visible:
            widget.widget.update()
            widget.widget.draw(self.camera)
