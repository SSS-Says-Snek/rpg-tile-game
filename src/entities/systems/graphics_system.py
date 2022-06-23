import pytmx
from src import pygame, screen, utils

from src.entities.systems.system import System
from src.entities import item_component, projectile_component
from src.entities.component import Flags, Graphics, Position, Movement, Inventory


class GraphicsSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list):
        screen.fill((180, 180, 180))
        # super().process(event_list)

        self.level_state.camera.adjust_to(
            self.world.component_for_entity(self.player, Position).pos
        )

        screen.blit(self.level_state.map_surface, self.level_state.camera.apply((0, 0)))

        # Mob blitting
        for entity, (graphics, pos) in self.world.get_components(Graphics, Position):
            if self.level_state.debug:
                tilemap = self.level_state.tilemap.tilemap

                for layer_id, layer in enumerate(tilemap.visible_layers):
                    if isinstance(layer, pytmx.TiledTileLayer):
                        for x, y, gid in layer:
                            # Adds tile props to dict
                            tile_props = tilemap.get_tile_properties_by_gid(gid)
                            if tile_props is None:
                                continue

                            pygame.draw.rect(
                                screen, (0, 255, 0),
                                self.level_state.camera.apply(
                                    pygame.Rect(x * tilemap.tilewidth, y * tilemap.tileheight,
                                                tilemap.tilewidth, tilemap.tileheight)
                                ), width=1
                            )

            if not self.world.component_for_entity(entity, Flags).rotatable:
                if self.level_state.debug:
                    pygame.draw.rect(screen, (255, 0, 0), self.level_state.camera.apply(pos.rect), width=1)

                if graphics.sprite is not None:
                    screen.blit(graphics.sprite, self.level_state.camera.apply(pos.pos))
                else:
                    screen.blit(graphics.sprites[graphics.sprites_state], self.level_state.camera.apply(pos.pos))
            else:
                movement = self.world.component_for_entity(entity, Movement)
                rotated_sprite, new_pos = utils.rot_center(
                    graphics.sprite, movement.rot,
                    *pygame.Rect(*pos.pos, *graphics.size).center
                )
                screen.blit(rotated_sprite, self.level_state.camera.apply(new_pos))

            # Blit weapon sprite
            if entity == self.player:
                inventory = self.world.component_for_entity(entity, Inventory)
                equipped_item = inventory.inventory[inventory.equipped_item_idx]

                if equipped_item is not None:
                    item_graphics = self.world.component_for_entity(equipped_item, item_component.ItemGraphics)
                    item_pos = self.world.component_for_entity(equipped_item, item_component.ItemPosition)
                    screen.blit(item_graphics.current_img, self.level_state.camera.apply(item_pos.pos))

        for entity, (item_graphics, item_pos) in self.world.get_components(
            item_component.ItemGraphics, item_component.ItemPosition
        ):
            if not item_pos.in_inventory:
                screen.blit(item_graphics.world_sprite, self.level_state.camera.apply(item_pos.pos))

        for entity, (projectile_graphics, projectile_pos) in self.world.get_components(
            projectile_component.ProjectileGraphics, projectile_component.ProjectilePosition
        ):
            screen.blit(projectile_graphics.current_img, self.level_state.camera.apply(projectile_pos.pos))
