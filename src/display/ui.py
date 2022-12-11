"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the UI class, used to handle... the game UI
"""
from __future__ import annotations

from typing import Optional, TypedDict

import esper

from src.display.camera import Camera
from src.display.particle import ParticleManager
from src.display.widgets.widget import Widget


class WidgetDict(TypedDict):
    widget: Widget
    visible: bool


class UI:
    def __init__(self, camera: Optional[Camera] = None):
        """
        A user interface manager for the entire game

        Args:
            camera: The game camera
        """

        self.current_widget_uuid = 0

        self.camera = camera
        self.world: Optional[esper.World] = None
        self.particle_system: Optional[ParticleManager] = None
        self.widgets: dict[int, WidgetDict] = {}
        self.hud_widgets: dict[str, WidgetDict] = {}

    def draw(self):
        """Draws all widgets"""

        for widget_dict in self.widgets.copy().values():
            widget = widget_dict["widget"]
            if not widget_dict["visible"]:
                continue

            if self.camera is not None:
                widget.draw(self.camera)
            else:
                widget.draw(None)

    def update(self):
        """Updates all widgets in the user interface"""

        for widget_dict in self.widgets.copy().values():
            widget = widget_dict["widget"]
            if not widget_dict["visible"]:
                continue

            widget.update()

    def add_widget(
        self,
        widget: Widget,
        hud: bool = False,
        hud_name: Optional[str] = None,
        visible: bool = True,
    ) -> int:
        """
        Adds a widget to the UI

        Args:
            widget: The widget to add
            hud: Whether or not it is a heads-up display widget
            hud_name: The HUD name to reference it elsewhere if it is a HUD widget
            visible: Whether it is currently visible or not

        Returns:
            An ID for the widget
        """

        widget.uuid = self.current_widget_uuid
        self.widgets[self.current_widget_uuid] = {"widget": widget, "visible": visible}
        if hud and hud_name:
            self.hud_widgets[hud_name] = {"widget": widget, "visible": visible}

        self.current_widget_uuid += 1
        return widget.uuid

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

        self.widgets[uuid]["visible"] = not self.widgets[uuid]["visible"]
