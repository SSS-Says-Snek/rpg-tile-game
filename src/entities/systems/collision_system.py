import pygame

from src import utils
from src.entities.systems.system import System
from src.entities.component import Position, Movement, Graphics, Flags, Tile

class CollisionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def collide_with_unwalkable_tiles(
        axis: str, unwalkable_rects, pos, vel, graphics
    ):
        rect = pygame.Rect(*pos.pos, *graphics.size)

        if axis == "x":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if vel.vx > 0:
                        pos.pos.x = unwalkable_rect.left - rect.width
                    elif vel.vx < 0:
                        pos.pos.x = unwalkable_rect.right
                    vel.vx = 0

        elif axis == "y":
            for unwalkable_rect in unwalkable_rects:
                if rect.colliderect(unwalkable_rect):
                    if vel.vy > 0:
                        pos.pos.y = unwalkable_rect.top - rect.height
                    elif vel.vy < 0:
                        pos.pos.y = unwalkable_rect.bottom
                    vel.vy = 0

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

            # Update where entity is facing
            """if movement.vx > 0:
                print("Facing right")
            elif movement.vx < 0:
                print("facing left")

            if movement.vy > 0:
                print("facing down")
            elif movement.vy < 0:
                print("facing up")"""

            if self.world.component_for_entity(entity, Flags).collidable:
                # Actual entity collision
                pos.pos.x += movement.vx * self.level_state.game_class.dt
                self.collide_with_unwalkable_tiles("x", unwalkable_tile_rects, pos, movement, graphics)
                pos.pos.y += movement.vy * self.level_state.game_class.dt
                self.collide_with_unwalkable_tiles("y", unwalkable_tile_rects, pos, movement, graphics)
                pos.tile_pos = utils.pixel_to_tile(pos.pos)
            else:
                # Entity movement without collision yet with movement
                pos.pos.x += movement.vx * self.level_state.game_class.dt
                pos.pos.y += movement.vy * self.level_state.game_class.dt

            if self.world.component_for_entity(entity, Flags).rotatable:
                movement.rot = (
                        self.world.component_for_entity(self.player, Position).pos - pos.pos
                ).angle_to(pygame.Vector2(1, 0))
