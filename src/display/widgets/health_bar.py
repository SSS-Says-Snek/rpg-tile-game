from src import pygame, screen

class HealthBar:
    def __init__(self, pos, width, height, health_component):
        self.pos = pos
        self.width = width
        self.height = height
        self.health_component = health_component

        self.border_rect = pygame.Rect(pos[0] - 2, pos[1] - 2, width + 4, height + 4)
        self.rect = pygame.Rect(*pos, self.health_component.hp / self.health_component.max_hp * width, height)

    def draw(self, _): # Camera not used
        self.rect.width = self.health_component.hp / self.health_component.max_hp * self.width

        pygame.draw.rect(screen, (128, 128, 0), self.border_rect, width=2)
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
