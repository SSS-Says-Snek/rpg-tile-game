"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from src import utils
from src.common import HEIGHT, IMG_DIR, WIDTH
from src.display.particle import ImageParticle
from src.entities.components import tile_component
from src.entities.systems.system import System

if TYPE_CHECKING:
    from src.states.level_state import LevelState


class ParticleGenSystem(System):
    def __init__(self, level_state: LevelState):
        super().__init__(level_state)

        self.wind_gusts = [-15, -15, -15]
        self.random_wind_gust_idx = random.randrange(0, len(self.wind_gusts))
        self.cloud_parallax = 0.3
        self.cloud_paths = list((IMG_DIR / "deco" / "clouds").iterdir())

    def create_wind_particles(self):
        # Adds wind gust particles
        if random.random() < 0.19:
            if random.random() < 0.05:
                self.wind_gusts = [random.uniform(-15, -1.5) for _ in range(3)]
                self.random_wind_gust_idx = random.randrange(0, len(self.wind_gusts))

            self.particle_manager.create_wind_particle(
                pygame.Vector2(
                    random.randint(self.camera.camera.x, self.camera.camera.x + WIDTH),
                    random.randint(self.camera.camera.y, self.camera.camera.y + HEIGHT),
                ),
                self.wind_gusts,
            )

    def create_tree_particles(self):
        for entity, (tile, tile_deco) in self.world.get_components(tile_component.Tile, tile_component.Decoration):
            if random.random() < 0.025:
                self.particle_manager.create_wind_particle(
                    pygame.Vector2(
                        random.randint(tile.rect.x, tile.rect.x + tile.rect.width),
                        random.randint(tile.rect.y, tile.rect.y + tile.rect.height),
                    ),
                    self.wind_gusts,
                    movement_factor=1.5,
                )

    def create_clouds(self):
        if random.random() < 0.015:
            self.particle_manager.add(
                ImageParticle()
                .builder()
                .at(
                    pygame.Vector2(
                        # MAGIC NUMBERS - DON'T QUESTION
                        # Gist: Spawns clouds at appropriate pos outside of screen
                        WIDTH + (self.camera.camera.x + WIDTH) * self.cloud_parallax + random.randint(-300, 400),
                        self.camera.camera.y * self.cloud_parallax + random.randint(-75, 125),
                    )
                )
                .image(
                    image=utils.load_img(random.choice(self.cloud_paths)),
                    scale=random.uniform(0.6, 1.1),
                )
                .starting_vel(
                    # - 0.3 is for semi-guarentee no lagging
                    pygame.Vector2(random.choice(self.wind_gusts) / random.uniform(13, 17) - 0.4, 0)
                )
                .lifespan(frames=2000)
                .draw_when(when="pre_interactables")
                .parallax(parallax_val=self.cloud_parallax)
                .effect_fade(start_fade_frac=0.9)
                .build()
            )

    def process(self):
        self.create_wind_particles()
        self.create_tree_particles()
        self.create_clouds()
