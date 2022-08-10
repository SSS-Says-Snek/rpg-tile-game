import math

from src import pygame, screen, utils
from src.common import WIDTH


class SignState:
    INACTIVE = 0
    TYPING = 1
    DONE = 2


class TileHover:
    def __init__(self, tile):
        self.x = tile.x * tile.tile_width
        self.y = (tile.y - 2) * tile.tile_height

        self.rect = pygame.Rect(self.x, self.y, tile.tile_width, tile.tile_height)

    def draw(self, camera):
        # Adjust bob
        rect_copy = self.rect.copy()
        rect_copy.y += round(math.sin(pygame.time.get_ticks() / 150) * 5)

        pygame.draw.rect(screen, (255, 0, 0), camera.apply(rect_copy))


class SignDialogue:
    def __init__(self, text):
        self.text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque rhoncus dictum orci, et fringilla nulla cursus sit amet. Pellentesque habitant morbi tristique senectus et netus et malesuada."

        self.width = 750
        self.height = 200

        self.font = utils.load_font(36, "ThaleahFat")
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (WIDTH // 2, 680)

        self.state = SignState.INACTIVE
        self.text_idxs = {"total": 0, "line": 0, "char": 0}
        self.update_text = utils.Task(25)

        self.wrapped_text = self.wrap_text(self.text)

    def wrap_text(self, text: str):
        wrapped_text = []

        # I can manually place newlines for ease
        split_text = text.split('\n')
        for line in split_text:
            words = line.split(' ')
            start, i = 0, 0

            # Checks word by word to see the longest possible line that doesn't exceed the width
            while i < len(words):
                if self.font.size(' '.join(words[start:i + 1]))[0] > self.width - 30:
                    wrapped_text.append(' '.join(words[start:i]))
                    start = i
                i += 1

            wrapped_text.append(' '.join(words[start:i]))

        return wrapped_text

    def blit_wrapped_text(self, wrapped_text):
        for i, wrapped_line in enumerate(wrapped_text):
            line_surf = self.font.render(wrapped_line, False, (0, 0, 0))
            screen.blit(
                line_surf,
                (self.rect.x + 15,
                 self.rect.y + 10 + i * self.font.get_height())
            )

    def draw(self, _):  # Static
        keys = pygame.key.get_pressed()
        if self.state == SignState.INACTIVE:
            if keys[pygame.K_e] or keys[pygame.K_RETURN]:
                self.state = SignState.TYPING
        else:
            if self.state == SignState.TYPING and self.update_text.update():
                # Handle indexing
                self.text_idxs["total"] += 1
                self.text_idxs["char"] += 1

                if self.text_idxs["char"] - 1 == len(self.wrapped_text[self.text_idxs["line"]]):
                    self.text_idxs["char"] = 0
                    self.text_idxs["line"] += 1
                if self.text_idxs["total"] == len(self.text) - 1:
                    self.state = SignState.DONE

            # Draw body of dialogue
            pygame.draw.rect(screen, (128, 128, 128), self.rect, border_radius=10)

            # Handle the typing
            wrap_text_copy = self.wrapped_text[:]
            wrap_text_copy = wrap_text_copy[:self.text_idxs["line"] + 1]
            wrap_text_copy[-1] = wrap_text_copy[-1][:self.text_idxs["char"] + 1]

            self.blit_wrapped_text(wrap_text_copy)