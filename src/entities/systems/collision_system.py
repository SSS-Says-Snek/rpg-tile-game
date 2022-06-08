import pygame

from src import utils
from src.entities.systems.system import System
from src.entities.component import Position, Movement, Graphics, Flags, Tile

class CollisionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def collide_with_unwalkable_tiles(
        axis: str, unwalkable_rects, pos, movement, graphics
    ):
        rect = pygame.Rect(*pos.pos, *graphics.size)

        if axis == "x":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if movement.vx > 0:
                        pos.pos.x = unwalkable_rect.left - rect.width
                    elif movement.vx < 0:
                        pos.pos.x = unwalkable_rect.right
                    movement.vx = 0

        elif axis == "y":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if movement.vy > 0:
                        pos.pos.y = unwalkable_rect.top - rect.height
                    elif movement.vy < 0:
                        pos.pos.y = unwalkable_rect.bottom
                    movement.vy = 0

    def get_unwalkable_rects(self, neighboring_tiles):
        unwalkable_tile_rects = []

        for tile_entity_dict in neighboring_tiles:
            tile_entity, tile_pos = tile_entity_dict
            tile = self.world.component_for_entity(tile_entity, Tile)

            if self.world.component_for_entity(tile_entity, Flags).collidable:
                unwalkable_tile_rect = pygame.Rect(
                    tile_pos["x"] * tile.tile_width, tile_pos["y"] * tile.tile_height,
                    tile.tile_width, tile.tile_height
                )
                unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects

    def process(self, event_list):
        # super().process(event_list)

        for entity, (pos, movement, graphics) in self.world.get_components(
            Position, Movement, Graphics
        ):
            neighboring_tile_entities = utils.get_neighboring_tile_entities(self.level_state.tilemap, 1, pos)
            unwalkable_tile_rects = self.get_unwalkable_rects(neighboring_tile_entities)

            # FOR NOW!!! SUPER INEFFICIENT
            for nested_entity, (nested_pos, nested_movement, nested_graphics) in self.world.get_components(
                Position, Movement, Graphics
            ):
                if nested_entity != entity:
                    nested_entity_rect = pygame.Rect(
                        *nested_pos.pos, *nested_graphics.size
                    )
                    unwalkable_tile_rects.append(nested_entity_rect)

            # Update where entity is facing
            """if movement.vx > 0:
                print("Facing right")
            elif movement.vx < 0:
                print("facing left")

            if movement.vy > 0:
                print("facing down")
            elif movement.vy < 0:
                print("facing up")"""

            # If no acceleration (like player), then acc will be 0
            dt = self.level_state.game_class.dt
            collidable = self.world.component_for_entity(entity, Flags).collidable

            pos.pos.x += movement.vx * dt + 0 * 0.5 * movement.acc.x * dt ** 2
            if collidable:
                self.collide_with_unwalkable_tiles("x", unwalkable_tile_rects, pos, movement, graphics)
            pos.pos.y += movement.vy * dt + 0 * 0.5 * movement.acc.y * dt ** 2
            if collidable:
                self.collide_with_unwalkable_tiles("y", unwalkable_tile_rects, pos, movement, graphics)
            pos.tile_pos = utils.pixel_to_tile(pos.pos)
            pos.rect = pygame.Rect(*pos.pos, *graphics.size)
