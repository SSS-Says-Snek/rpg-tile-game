from src import pygame, common
from src.tilemap import TileMap
from src.entities.mobs.player import Player
from src.display.camera import Camera

from .state import State

class LevelState(State):
    def __init__(self, game_class):
        super().__init__(game_class)

        self.camera = Camera(common.WIDTH, common.HEIGHT)

        self.tilemap = TileMap(common.MAP_DIR / "first_map.tmx")
        self.map_surface = self.tilemap.make_map()

        # self.entities includes player
        self.player = Player((400, 800), self.game_class, self)
        self.entities: dict[str, list] = {"player": [self.player]}

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.map_surface, self.camera.apply((0, 0)))

        for entity_list in self.entities.values():
            for entity in entity_list:
                entity.draw(self.camera)
                entity.update()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.change_state("level_state.TestState")

        for entity_list in self.entities.values():
            for entity in entity_list:
                entity.handle_event(event)

    def update(self):
        self.camera.adjust_to(self.player.rect)


class TestState(State):
    def draw(self):
        self.screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.change_state("level_state.LevelState")
