from src.common import TILE_WIDTH, TILE_HEIGHT

def pixel_to_tile(pixel_pos, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    # return pixel_pos[0] // tile_width, pixel_pos[1] // tile_height
    return round(pixel_pos[0] / tile_width), round(pixel_pos[1] / tile_height)

def tile_to_pixel(tile_pos, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    return tile_pos[0] * tile_width, tile_pos[1] * tile_height