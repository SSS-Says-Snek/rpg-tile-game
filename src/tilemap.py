import pathlib
import pygame
import pytmx

class TileMap:
    def __init__(self, map_path: pathlib.Path):
        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        # Tiles will be filled in on render_map
        self.tiles = {}

    def render_map(self, surface: pygame.Surface) -> None:
        for layer_id, layer in enumerate(self.tilemap.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Adds tile props to dict
                    self.tiles[(layer_id, (x, y))] = self.tilemap.get_tile_properties_by_gid(gid)
                    tile_img = self.tilemap.get_tile_image_by_gid(gid)
                    if tile_img:
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
