import pygame


class Time:
    def __init__(self):
        self.offsetted_time = 0

        self.pause_time = 0
        self.paused = False

    def get_ticks(self):
        if not self.paused:
            return pygame.time.get_ticks() - self.offsetted_time
        return self.pause_time

    def pause(self):
        if not self.paused:
            self.pause_time = pygame.time.get_ticks() - self.offsetted_time
            self.paused = True

    def unpause(self):
        if self.paused:
            self.offsetted_time = pygame.time.get_ticks() - self.pause_time
            self.paused = False
