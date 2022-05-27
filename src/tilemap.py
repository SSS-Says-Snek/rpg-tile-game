import pygame
import pytmx
import pathlib

class TileMap:
    def __init__(self, map_path: pathlib.Path):
        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

    def render_map(self, surface: pygame.Surface) -> None:
        for layer in self.tilemap.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tilemap.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(
                            tile,
                            (x * self.tilemap.tilewidth,
                             y * self.tilemap.tileheight)
                        )

    def make_map(self) -> pygame.Surface:
        temp_surface = pygame.Surface((self.width, self.height))
        self.render_map(temp_surface)
        return temp_surface
