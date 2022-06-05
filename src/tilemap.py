import pathlib
import pygame
import pytmx

from src.entities.component import *


class TileMap:
    def __init__(self, map_path: pathlib.Path, ecs_world):
        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        self.ecs_world = ecs_world

        # Tiles will be filled in on render_map
        self.tiles = {}
        self.entity_tiles = {}

    def render_map(self, surface: pygame.Surface) -> None:
        for layer_id, layer in enumerate(self.tilemap.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Adds tile props to dict
                    tile_props = self.tilemap.get_tile_properties_by_gid(gid)
                    if tile_props is None:
                        continue

                    self.tiles[(layer_id, (x, y))] = tile_props
                    tile_img = self.tilemap.get_tile_image_by_gid(gid)
                    components = [Tile(tile_props["width"], tile_props["height"])]

                    if tile_props.get("unwalkable"):
                        components.append(Collidable())

                    if tile_props.get("type") == "dialogue":
                        components.append(HasDialogue())

                    entity_id = self.ecs_world.create_entity(*components)
                    self.entity_tiles[(layer_id, (x, y))] = entity_id

                    surface.blit(
                        tile_img,
                        (x * self.tilemap.tilewidth,
                         y * self.tilemap.tileheight)
                    )

    def make_map(self) -> pygame.Surface:
        temp_surface = pygame.Surface((self.width, self.height))
        self.render_map(temp_surface)
        return temp_surface

    def get_visible_tile_layers(self):
        return [
            layer for layer in self.tilemap.visible_layers
            if isinstance(layer, pytmx.TiledTileLayer)
        ]
