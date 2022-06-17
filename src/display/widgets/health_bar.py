from src import pygame, screen

from src.entities.component import Position, Health


class PlayerHealthBar:
    def __init__(self, ui, entity, pos, width, height, border_width=2):
        self.uuid = None
        self.ui = ui
        self.entity = entity

        self.pos = pos
        self.width = width
        self.height = height
        self.border_width = border_width
        self.health_component = self.ui.world.component_for_entity(self.entity, Health)

        self.border_rect = pygame.Rect(
            pos[0] - border_width, pos[1] - border_width,
            width + 2 * border_width, height + 2 * border_width
        )
        self.rect = pygame.Rect(*pos, self.health_component.hp / self.health_component.max_hp * width, height)

    def draw(self, *_): # Both camera and UI not used
        self.rect.width = self.health_component.hp / self.health_component.max_hp * self.width

        pygame.draw.rect(screen, (0, 0, 0), self.border_rect, width=self.border_width)
        pygame.draw.rect(screen, (0, 255, 0), self.rect)


class MobHealthBar:
    def __init__(self, ui, entity, width, height, border_width=2):
        self.uuid = None
        self.ui = ui
        self.entity = entity

        self.pos = self.ui.world.component_for_entity(entity, Position)
        self.width = width
        self.height = height
        self.border_width = border_width
        self.health_component = self.ui.world.component_for_entity(self.entity, Health)

        self.border_rect = pygame.Rect(
            self.pos.pos.x - border_width, self.pos.pos.y - 20 - border_width,
            width + 2 * border_width, height + 2 * border_width
        )
        self.rect = pygame.Rect(*self.pos.pos, self.health_component.hp / self.health_component.max_hp * width, height)

    def draw(self, camera):
        if self.health_component.hp <= 0:
            self.ui.remove_widget(self.uuid)
            return
        entity_rect = self.pos.rect
        self.border_rect.center = (entity_rect.centerx - self.border_width, entity_rect.centery - 20 - self.border_width)
        self.rect.topleft = (self.border_rect.x + self.border_width, self.border_rect.y + self.border_width)
        self.rect.width = self.health_component.hp / self.health_component.max_hp * self.width

        pygame.draw.rect(screen, (0, 0, 0), camera.apply(self.border_rect), width=self.border_width)
        pygame.draw.rect(screen, (0, 255, 0), camera.apply(self.rect))

