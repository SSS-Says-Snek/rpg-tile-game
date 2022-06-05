from src.common import TILE_WIDTH, TILE_HEIGHT

def pixel_to_tile(pixel_pos, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    # return pixel_pos[0] // tile_width, pixel_pos[1] // tile_height
    return [round(pixel_pos[0] / tile_width), round(pixel_pos[1] / tile_height)]

def tile_to_pixel(tile_pos, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    return [tile_pos[0] * tile_width, tile_pos[1] * tile_height]


def get_neighboring_tile_entities(tilemap, radius, pos):
    neighboring_tile_entities = []

    for layer_id in range(len(tilemap.get_visible_tile_layers())):
        for x in range(pos.tile_pos[0] - radius, pos.tile_pos[0] + radius + 1):
            for y in range(pos.tile_pos[1] - radius, pos.tile_pos[1] + radius + 1):
                try:
                    tile_entity = tilemap.entity_tiles[(layer_id, (x, y))]
                except KeyError:
                    # Outside map boundaries (for some reason)
                    continue

                neighboring_tile_entities.append((tile_entity, {"x": x, "y": y}))

    return neighboring_tile_entities