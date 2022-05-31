import esper
import pygame

from src import utils

from src.entities.components.velocity import Velocity
from src.entities.components.position import Position
from src.entities.components.graphics import Graphics
from src.entities.components.collision import Collidable

class CollisionSystem(esper.Processor):
    def __init__(self, level_state):
        super().__init__()

        self.level_state = level_state

    @staticmethod
    def collide_with_unwalkables(
        axis: str, unwalkable_rects, pos, vel, graphics
    ):
        rect = pygame.Rect(*pos.pos, *graphics.size)

        if axis == "x":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if vel.vx > 0:
                        pos.pos[0] = unwalkable_rect.left - rect.width
                    elif vel.vx < 0:
                        pos.pos[0] = unwalkable_rect.right
                    vel.vx = 0

        elif axis == "y":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if vel.vy > 0:
                        pos.pos[1] = unwalkable_rect.top - rect.height
                    elif vel.vy < 0:
                        pos.pos[1] = unwalkable_rect.bottom
                    vel.vy = 0

    def get_unwalkable_rects(self, pos) -> list[pygame.Rect]:
        unwalkable_tile_rects = []
        # Loop through all layers and all tiles within 1 tile of player
        for layer_id in range(len(self.level_state.tilemap.get_visible_tile_layers())):
            for i in range(pos.tile_pos[0] - 1, pos.tile_pos[0] + 2):
                for j in range(pos.tile_pos[1] - 1, pos.tile_pos[1] + 2):
                    try:
                        tile = self.level_state.tilemap.tiles[(layer_id, (i, j))]
                    except KeyError:
                        # Outside map boundaries
                        continue
                    if tile is not None and tile["unwalkable"]:
                        unwalkable_tile_rect = pygame.Rect(
                            i * tile["width"], j * tile["height"],
                            tile["width"], tile["height"]
                        )
                        unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects

    def process(self):
        for entity, (collidable, pos, vel, graphics) in self.world.get_components(
            Collidable, Position, Velocity, Graphics
        ):
            unwalkable_tile_rects = self.get_unwalkable_rects(pos)

            pos.pos[0] += vel.vx * self.level_state.game_class.dt
            self.collide_with_unwalkables("x", unwalkable_tile_rects, pos, vel, graphics)
            pos.pos[1] += vel.vy * self.level_state.game_class.dt
            self.collide_with_unwalkables("y", unwalkable_tile_rects, pos, vel, graphics)

            pos.tile_pos = utils.pixel_to_tile(pos.pos)
