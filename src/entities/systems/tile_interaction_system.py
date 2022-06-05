from src import pygame, screen, utils
from src.entities.systems.system import System
from src.entities.component import *

class TestBlit:
    def __init__(self):
        self.text = "OMGGGGG"

        self.txt_surf = pygame.font.SysFont("arial", 24).render("OMG", True, (0, 0, 0))

    def draw(self, camera):
        screen.blit(self.txt_surf, camera.apply((400, 400)))

class TileInteractionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def get_event(event_list, event_type):
        for event in event_list:
            if event.type == event_type:
                return event

    def check_for_key(self, event_list, key, event_type=pygame.KEYDOWN):
        event = self.get_event(event_list, event_type)
        if event is not None and event.key == key:
            return True
        return False

    def process(self, event_list):
        # super().process(event_list)

        for entity, (pos, *_) in self.world.get_components(Position, Velocity):
            neighboring_tile_entities = utils.get_neighboring_tile_entities(self.level_state.tilemap, 2, pos)

            for neighboring_tile_entity in neighboring_tile_entities:
                if self.world.has_component(neighboring_tile_entity[0], HasDialogue):
                    if self.check_for_key(event_list, pygame.K_RETURN):
                        self.level_state.ui.add_widget(TestBlit())
