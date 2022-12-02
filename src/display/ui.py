"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the UI class, used to handle... the game UI
"""
from __future__ import annotations

from typing import Optional

import esper

from src.display.camera import Camera
from src.display.particle import ParticleManager
from src.display.widgets.widget import Widget
from src.types import Dts, Events


class UI:
    def __init__(self, camera: Optional[Camera]):
        self.current_widget_uuid = 0

        self.camera = camera
        self.world: Optional[esper.World] = None
        self.particle_system: Optional[ParticleManager] = None
        self.widgets = {}
        self.hud_widgets = {}

    def draw(self):
        for widget_dict in self.widgets.copy().values():
            widget = widget_dict["widget"]
            if not widget_dict["visible"]:
                continue

            if self.camera is not None:
                widget.draw(self.camera)
            else:
                widget.draw()

    def update(self, event_list: Events, dts: Dts):
        for widget_dict in self.widgets.copy().values():
            widget = widget_dict["widget"]
            if not widget_dict["visible"]:
                continue

            widget.update(event_list, dts)

    def add_widget(
        self,
        widget: Widget,
        hud: bool = False,
        hud_name: Optional[str] = None,
        visible: bool = True,
    ):
        widget.uuid = self.current_widget_uuid
        self.widgets[self.current_widget_uuid] = {"widget": widget, "visible": visible}
        if hud and hud_name:
            self.hud_widgets[hud_name] = {"widget": widget, "visible": visible}

        self.current_widget_uuid += 1
        return widget.uuid

    def remove_widget(self, uuid: int):
        del self.widgets[uuid]

    def toggle_visible(self, uuid: int):
        self.widgets[uuid]["visible"] = not self.widgets[uuid]["visible"]
