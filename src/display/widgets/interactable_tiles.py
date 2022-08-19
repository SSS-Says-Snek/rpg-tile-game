"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

import math

from src import pygame, screen, utils
from src.common import IMG_DIR, TILE_HEIGHT, TILE_WIDTH, WIDTH
from src.display.widgets.widget import Widget


def create_tile_hover_surf(font):
    surf = pygame.Surface((TILE_WIDTH + 4, TILE_HEIGHT + 4), pygame.SRCALPHA)
    pygame.draw.rect(surf, (249, 204, 127), ((0, 0), surf.get_size()), border_radius=5)
    pygame.draw.rect(surf, (80, 46, 23), ((0, 0), surf.get_size()), width=2, border_radius=5)

    txt_surf = font.render("E", True, (0, 0, 0))
    txt_surf_rect = txt_surf.get_rect(center=(TILE_WIDTH // 2 + 2, TILE_HEIGHT // 2 + 1))
    surf.blit(txt_surf, txt_surf_rect)

    return surf


class SignState:
    INACTIVE = 0
    TYPING = 1
    DONE = 2


class TileHover(Widget):
    FONT = utils.load_font(32)
    SURF = create_tile_hover_surf(FONT)

    def __init__(self, tile):
        self.x = tile.x * tile.tile_width
        self.y = tile.y * tile.tile_height
        self.hover_y = self.y - 2 * tile.tile_height

        self.rect = pygame.Rect(self.x, self.hover_y, tile.tile_width, tile.tile_height)

    def draw(self, camera):
        # Adjust bob
        rect_copy = self.rect.copy()
        rect_copy.y += round(math.sin(pygame.time.get_ticks() / 150) * 5)

        screen.blit(self.SURF, camera.apply(rect_copy))
        # screen.blit(self.outline, camera.apply(self.x, self.y))


class SignDialogue(Widget):
    DIALOGUE_BACKGROUND = utils.load_img(IMG_DIR / "misc" / "dialogue_background.png")
    DIALOGUE_BACKGROUND_RECT = DIALOGUE_BACKGROUND.get_rect(center=(WIDTH // 2, 680))

    def __init__(self, text):
        self.text = text
        self.width = 750
        self.height = 200
        self.x_offset = 50

        self.font = utils.load_font(16, "Minecraftia")
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (WIDTH // 2, 680)

        self.state = SignState.INACTIVE
        self.text_idxs = {"total": 0, "line": 0, "char": 0}
        self.update_text = utils.Task(25)

        self.show_cursor = True
        self.cursor_blink = utils.Task(500)

        self.wrapped_text = self.wrap_text(self.text)

    def wrap_text(self, text: str):
        wrapped_text = []

        # I can manually place newlines for ease
        split_text = text.split("\n")
        for line in split_text:
            words = line.split(" ")
            start, i = 0, 0

            # Checks word by word to see the longest possible line that doesn't exceed the width
            while i < len(words):
                if (
                    self.font.size(" ".join(words[start : i + 1]))[0]
                    > self.width - 2 * self.x_offset
                ):
                    wrapped_text.append(" ".join(words[start:i]))
                    start = i
                i += 1

            wrapped_text.append(" ".join(words[start:i]))

        return wrapped_text

    def blit_wrapped_text(self, wrapped_text):
        x, y = 0, 0
        line_surf = None

        for i, wrapped_line in enumerate(wrapped_text):
            line_surf = self.font.render(wrapped_line, False, (78, 53, 36))
            x, y = self.rect.x + self.x_offset, self.rect.y + 35 + i * self.font.get_height() * 1.3
            screen.blit(line_surf, (x, y))

        if line_surf is not None and self.show_cursor:
            # Utilizes last line to get cursor pos
            pygame.draw.rect(
                screen,
                (78, 53, 36),
                (x + line_surf.get_width(), y, 2, line_surf.get_height() * 4 / 5),
            )

    def update(self, event_list, dts):
        for event in event_list:
            if (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_e, pygame.K_RETURN)
                and self.update_text.time_passed(50)
            ):
                if self.state == SignState.INACTIVE:
                    self.state = SignState.TYPING
                elif self.state == SignState.TYPING:
                    self.state = SignState.DONE
                    self.text_idxs["char"] = len(self.wrapped_text[-1]) - 1
                    self.text_idxs["line"] = len(self.wrapped_text) - 1
                elif self.state == SignState.DONE:
                    self.state = SignState.INACTIVE
                    self.text_idxs = {"total": 0, "line": 0, "char": 0}

                self.update_text.update_time()

    def draw(self, _):  # Static
        # Handle indexing
        if self.state != SignState.INACTIVE:
            if self.state == SignState.TYPING and self.update_text.update():
                self.text_idxs["total"] += 1
                self.text_idxs["char"] += 1

                # If going onto new line
                if self.text_idxs["char"] - 1 == len(self.wrapped_text[self.text_idxs["line"]]):
                    self.text_idxs["char"] = 0
                    self.text_idxs["line"] += 1
                if self.text_idxs["total"] == len(self.text) - 1:
                    self.state = SignState.DONE
            elif self.state == SignState.DONE and self.cursor_blink.update():
                self.show_cursor = not self.show_cursor

            # Draw body of dialogue
            # pygame.draw.rect(screen, (128, 128, 128), self.rect, border_radius=10)
            screen.blit(self.DIALOGUE_BACKGROUND, self.DIALOGUE_BACKGROUND_RECT)

            # Handle the typing
            wrap_text_copy = self.wrapped_text
            wrap_text_copy = wrap_text_copy[: self.text_idxs["line"] + 1]
            wrap_text_copy[-1] = wrap_text_copy[-1][: self.text_idxs["char"] + 1]

            self.blit_wrapped_text(wrap_text_copy)
