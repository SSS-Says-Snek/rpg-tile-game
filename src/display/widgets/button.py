"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains buttons, whether in-game or for menus
"""

from __future__ import annotations

from typing import Optional

from src import core, pygame, screen, utils
from src.display.transition import EaseTransition
from src.display.ui import UI
from src.display.widgets.widget import Widget
from src.types import Pos, TupColor, TupSize, VoidFunc


class DefaultButton(Widget):
    """A static button, used for UIs and Menus"""

    def __init__(
        self,
        ui: UI,
        pos: Pos,
        size: TupSize,
        color: TupColor = (128, 128, 128),
        text: Optional[str] = None,
        text_size: int = 20,
        text_color: TupColor = (0, 0, 0),
        border_width: int = 0,
        border_color: TupColor = (60, 60, 60),
        border_roundness: int = 0,
        hover_color: Optional[TupColor] = None,
        fade_duration: int = 500,
        click_callback: Optional[VoidFunc] = None,
        fade_callback: Optional[VoidFunc] = None,
        screen: pygame.Surface = screen
    ):
        super().__init__()

        self.ui = ui
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos, self.size)
        self.interact_rect = self.rect

        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        self.hover_color = hover_color
        self.text = text
        self.text_size = text_size
        self.border_width = border_width
        self.border_roundness = border_roundness

        self.click_callback = click_callback
        self.fade_callback = fade_callback

        self.border_clicked = False
        self.border_fade = EaseTransition(
            255, 0, fade_duration, EaseTransition.ease_out_quad, default_end=0, callback=self._fade_callback
        )
        self.border_expand = EaseTransition(0, 40, fade_duration, EaseTransition.ease_out_cub, default_end=40)

        if self.text:
            text_font = utils.load_font(self.text_size)
            self.text_surf = text_font.render(self.text, True, self.text_color)
            self.text_surf_center = self.text_surf.get_rect(center=self.rect.center)
        else:
            self.text_surf = None
            self.text_surf_center = None

        self.screen = screen

    def _fade_callback(self):
        self.border_clicked = False

        if self.fade_callback is not None:
            self.fade_callback()

    def _draw_border_effect(self):
        border_effect = self.border_expand.value or 0
        border_effect_size = (self.rect.width + border_effect, self.rect.height + border_effect)
        fade_surf = pygame.Surface(border_effect_size, pygame.SRCALPHA)
        fade_surf.set_alpha(self.border_fade.value if self.border_fade.value is not None else 255)

        pygame.draw.rect(
            fade_surf,
            (180, 211, 233),
            fade_surf.get_rect(),
            border_radius=self.border_roundness * 2,
        )
        self.screen.blit(fade_surf, fade_surf.get_rect(center=self.rect.center))

        self.border_fade.update()
        self.border_expand.update()

    def draw(self, *_):
        if self.border_clicked:
            self._draw_border_effect()

        # Border
        if self.hover_color is not None and self.rect.collidepoint(pygame.mouse.get_pos()):
            bg_color = self.hover_color
        else:
            bg_color = self.color
        pygame.draw.rect(self.screen, bg_color, self.rect, border_radius=self.border_roundness)

        # Main rect
        pygame.draw.rect(
            self.screen,
            self.border_color,
            self.rect,
            width=self.border_width,
            border_radius=self.border_roundness,
        )

        if self.text_surf is not None:
            self.screen.blit(self.text_surf, self.text_surf_center)

    def update(self):
        for event in core.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos) and not self.border_clicked:
                self.border_clicked = True
                self.border_fade.start()
                self.border_expand.start()

                if self.click_callback is not None:
                    self.click_callback()
