from src import pygame, screen, utils
from src.entities.systems.system import System
from src.entities.component import Flags, Graphics, Position, Movement


class GraphicsSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list):
        # super().process(event_list)

        self.level_state.camera.adjust_to(
            self.world.component_for_entity(self.player, Position).pos
        )

        for entity, (graphics, pos) in self.world.get_components(Graphics, Position):
            if not self.world.component_for_entity(entity, Flags).rotatable:
                screen.blit(graphics.sprite, self.level_state.camera.apply(pos.pos))
            else:
                movement = self.world.component_for_entity(entity, Movement)
                rotated_sprite, new_pos = utils.rot_center(
                    graphics.sprite, movement.rot,
                    *pygame.Rect(*pos.pos, *graphics.size).center
                )
                screen.blit(rotated_sprite, self.level_state.camera.apply(new_pos))