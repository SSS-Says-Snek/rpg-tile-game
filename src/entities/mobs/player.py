from src import pygame, screen, utils
from src.entities.entity import Entity

class Player(Entity):
    PLAYER_SPEED = 250

    def __init__(self, pos, game_class, state):
        super().__init__(game_class, state)

        self.pos = pos
        self.tile_pos = utils.pixel_to_tile(self.pos)
        self.sprite = pygame.Rect(self.pos[0], self.pos[1], 16, 16)
        self.rect = self.sprite

        self.vx, self.vy = 0, 0

    def update_velocities(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.vy = -self.PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.vy = self.PLAYER_SPEED
        if keys[pygame.K_LEFT]:
            self.vx = -self.PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vx = self.PLAYER_SPEED

        if self.vx and self.vy:
            # Adjust diagonal speed to match normal
            self.vx *= 0.707
            self.vy *= 0.707

    def get_unwalkable_rects(self):
        unwalkable_tile_rects = []
        for i in range(self.tile_pos[0] - 1, self.tile_pos[0] + 2):
            for j in range(self.tile_pos[1] - 1, self.tile_pos[1] + 2):
                try:
                    tile = self.state.tilemap.tilemap.get_tile_properties(i, j, 0)
                except (Exception, ValueError):
                    # Don't flame me it's pytmx that raises Exception
                    continue
                if tile["unwalkable"]:
                    unwalkable_tile_rect = pygame.Rect(
                        i * tile["width"], j * tile["height"],
                        tile["width"], tile["height"]
                    )
                    unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects

    def collide_with_unwalkables(self, direction, unwalkable_rects):
        if direction == "x":
            for unwalkable_rect in unwalkable_rects:
                if self.sprite.colliderect(unwalkable_rect):
                    if self.vx > 0:
                        self.sprite.x = unwalkable_rect.left - self.sprite.width
                        # print("right", self.sprite.x, self.sprite.y)
                    elif self.vx < 0:
                        self.sprite.x = unwalkable_rect.right
                        # print("left", self.sprite.x, self.sprite.y)
                    self.vx = 0
                    self.pos[0] = self.sprite.x

        elif direction == "y":
            for unwalkable_rect in unwalkable_rects:
                if self.sprite.colliderect(unwalkable_rect):
                    if self.vy > 0:
                        self.sprite.y = unwalkable_rect.top - self.sprite.height
                        # print("down", self.sprite.x, self.sprite.y)
                    elif self.vy < 0:
                        self.sprite.y = unwalkable_rect.bottom
                        # print("up", self.sprite.x, self.sprite.y)
                    self.vy = 0
                    self.pos[1] = self.sprite.y

    def draw(self, camera):
        pygame.draw.rect(screen, (255, 0, 0), camera.apply(self.sprite))

    def update(self):
        self.update_velocities()

        unwalkable_tile_rects = []
        if self.vx or self.vy:
            self.pos = [self.sprite.x, self.sprite.y]
            self.tile_pos = utils.pixel_to_tile(self.pos)

            unwalkable_tile_rects = self.get_unwalkable_rects()

        self.sprite.x += self.vx * self.game_class.dt
        self.collide_with_unwalkables("x", unwalkable_tile_rects)
        self.sprite.y += self.vy * self.game_class.dt
        self.collide_with_unwalkables("y", unwalkable_tile_rects)

    def handle_event(self, event):
        pass
