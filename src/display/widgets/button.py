"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import Callable, Optional

from src import pygame, screen
from src.display.ui import UI
from src.display.widgets.widget import Widget


class DefaultButton(Widget):
    """A static button, used for UIs and Menus"""

    def __init__(
        self,
        ui: UI,
        pos: tuple[int, int],
        size: tuple[int, int],
        color: tuple[int, int, int] = (128, 128, 128),
        text: Optional[str] = None,
        text_size: int = 20,
        text_color: tuple[int, int, int] = (0, 0, 0),
        border_width: Optional[int] = None,
        border_color: tuple[int, int, int] = (60, 60, 60),
        border_roundness: int = 0,
        hover_color: Optional[tuple[int, int, int]] = None,
        click_callback: Optional[Callable[[], None]] = None,
    ):
        self.ui = ui
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos, self.size)

        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        self.hover_color = hover_color
        self.text = text
        self.text_size = text_size
        self.border_width = border_width
        self.border_roundness = border_roundness

        self.click_callback = click_callback

    def draw(self, *_):
        if self.hover_color is not None and self.rect.collidepoint(pygame.mouse.get_pos()):
            bg_color = self.hover_color
        else:
            bg_color = self.color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.border_roundness)

        if self.border_width is not None:
            pygame.draw.rect(
                screen,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.border_roundness,
            )
