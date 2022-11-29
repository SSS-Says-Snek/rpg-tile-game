"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the implementation of the Particle system as well as particles.
I decided for particles to NOT be ECS entities.
"""
from __future__ import annotations

import math
import random
from math import cos, radians, sin
from typing import Callable, Optional, Union

import pygame.gfxdraw

from src import pygame, screen, utils
from src.display.camera import Camera
from src.entities.components.component import Position
from src.types import Color


class ParticleSystem(set):
    def __init__(self, camera: Camera, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = camera
        self.draw = self.draw_pre_ui

    def add(self, element, num_particles: int = 1):
        for _ in range(num_particles):
            super().add(element)

    def update(self):
        dead_particles = set()

        for particle in self:
            particle.update()

            if not particle.alive:
                dead_particles.add(particle)

        self.difference_update(dead_particles)

    #############################################################################################
    # DRAWING FUNCTIONS: If drawing particles not on LevelState, just use ParticleSystem.draw() #
    #############################################################################################

    def _draw_base(self, draw_when: str):
        for particle in self:
            if particle.draw_when == draw_when:
                particle.draw(self.camera)

    def draw_pre_interactables(self):
        self._draw_base("pre_interactables")

    def draw_pre_tilemap(self):
        self._draw_base("pre_tilemap")

    def draw_pre_ui(self):
        self._draw_base("pre_ui")

    def draw_post_ui(self):
        self._draw_base("post_ui")

    def create_hit_particles(self, num_particles: int, pos: Position, color_list: list[Color]):
        self.add(
            Particle()
            .builder()
            .at(pos=pos.pos, angle=random.gauss(180, 180))
            .color(color=random.choice(color_list))
            .gravity(gravity_acc=0.35, gravity_y_vel=-3.5)
            .lifespan(frames=40)
            .angular_speed(speed=random.gauss(1.4, 0.8))
            .effect_fade(start_fade_frac=0.5)
            .build(),
            num_particles=num_particles
        )

    def create_effect_particle(
        self,
        color_func: Callable[[], tuple[float, float]],
        pos: pygame.Vector2,
        angle_gauss: tuple[float, float] = (180, 140),
        offset: tuple[float, float] = (0, 0),
    ):
        self.add(
            Particle()
            .builder()
            .at(pygame.Vector2(pos.x + offset[0], pos.y + offset[1]), random.gauss(*angle_gauss))
            .gravity(gravity_acc=0.35, gravity_y_vel=-5)
            .hsv(*color_func())
            .lifespan(frames=40)
            .angular_speed(speed=random.gauss(1.4, 0.8))
            .effect_fade(start_fade_frac=0.5)
            .build()
        )

    def create_fire_particle(self, pos: pygame.Vector2, offset: tuple[float, float] = (0, 0)):
        self.create_effect_particle(lambda: (random.gauss(20, 20), random.gauss(1, 0.1)), pos, offset=offset)

    def create_regen_particle(self, pos: pygame.Vector2, offset: tuple[float, float] = (0, 0)):
        self.create_effect_particle(lambda: (random.gauss(120, 20), random.gauss(1, 0.08)), pos, offset=offset)

    def create_text_particle(self, pos: pygame.Vector2, txt: str, color: tuple[int, int, int] = (0, 0, 0)):
        self.add(
            TextParticle()
            .builder()
            .at(pos=pos)
            .color(color=color)
            .starting_vel(starting_vel=pygame.Vector2(0, -3))
            .lifespan(frames=30)
            .size(size=20)
            .text(text=txt)
            .effect_easeout_drift(easeout_speed=0.93)
            .effect_fade(start_fade_frac=0.5)
            .build()
        )

    def create_wind_particle(self, pos: pygame.Vector2, wind_gusts: list[float], movement_factor: float = 1):
        self.add(
            WindParticle()
            .builder()
            .at(pos)
            .starting_vel(pygame.Vector2(random.choice(wind_gusts), random.uniform(0.3, 1.8)) / movement_factor)
            .hsv(random.gauss(120, 20), random.gauss(1, 0.2))
            .lifespan(500)
            .size(random.randint(4, 7))
            .build()
        )


class Particle:
    """
    Arguments are NOT passed to particles via instantiation.
    Instead, there is a builder
    """

    def __init__(self):
        # Default values
        self.pos = pygame.Vector2(0, 0)
        self.draw_pos = pygame.Vector2(0, 0)
        self.starting_vel = pygame.Vector2(0, 0)
        self.vel = pygame.Vector2(0, 0)
        self.per_frame_vel = pygame.Vector2(0, 0)
        self.color = pygame.Color(0, 0, 0, 255)
        self.angle = 0
        self.angular_speed = None
        self.lifespan = None
        self.size = 10
        self.gravity = 0
        self.parallax_val = None

        self.alive = True
        self.static = False
        self.draw_when = "pre_ui"
        self.life = 0
        self.gravity_vel = 0
        self.effects = set()
        self.effects_extra_args = {}

    class Builder:
        def __init__(self, particle):
            self.particle = particle

        # ATTRIBUTE SETTERS

        def at(self, pos: pygame.Vector2, angle: float = 0):
            self.particle.pos = pos.copy()
            self.particle.angle = angle
            return self

        def color(self, color: Union[pygame.Color, tuple[int, int, int]]):
            self.particle.color = pygame.Color(color)
            return self

        def draw_when(self, when: str):
            self.particle.draw_when = when
            return self

        def gravity(self, gravity_acc: float, gravity_y_vel: float = 0):
            self.particle.gravity = gravity_acc
            self.particle.gravity_vel = gravity_y_vel
            return self

        def hsv(self, hue: float, saturation: float = 1.0, value: float = 1.0):
            h = round(hue) % 360
            s = max(min(round(100 * saturation), 100), 0)
            v = max(min(round(100 * value), 100), 0)
            self.particle.color.hsva = (h, s, v, 100)
            return self

        def lifespan(self, frames: Union[int, None]):
            self.particle.lifespan = frames
            return self

        def parallax(self, parallax_val: float):
            self.particle.parallax_val = parallax_val
            return self

        def size(self, size: float):
            self.particle.size = size
            return self

        def angular_speed(self, speed: float):
            self.particle.angular_speed = speed
            return self

        def starting_vel(self, starting_vel: pygame.Vector2):
            self.particle.vel = starting_vel.copy()
            self.particle.starting_vel = starting_vel.copy()
            return self

        def static(self):
            self.particle.static = True
            return self

        # CUSTOM EFFECTS

        def _effect(self, effect: Callable, *args):
            self.particle.effects.add(effect)
            self.particle.effects_extra_args[effect] = args
            return self

        def effect_fade(self, start_fade_frac: float = 0):
            def fade(particle):
                start_fade = start_fade_frac * particle.lifespan
                if particle.life < start_fade:
                    return

                adj_alpha = (particle.life - start_fade) / (particle.lifespan - start_fade)
                particle.color.a = max(min(int((1 - adj_alpha) * 255), 255), 0)

            return self._effect(fade)

        def build(self):
            return self.particle

    def builder(self):
        return self.Builder(self)

    def update(self):
        self.life += 1
        self.gravity_vel += self.gravity

        if self.angular_speed is not None:
            self.pos += (
                cos(radians(self.angle)) * self.angular_speed,
                sin(radians(self.angle)) * self.angular_speed,
            )
        self.pos += self.vel
        self.pos.y += self.gravity_vel
        self.draw_pos = self.pos.copy()

        if (
            (self.lifespan is not None and self.life >= self.lifespan)
            or (self.angular_speed is not None and self.angular_speed <= 0)
            or self.size <= 0
            or self.color.a == 0
        ):
            self.alive = False

        for effect in self.effects:
            effect(self)

        self.per_frame_vel.update()

    def draw(self, camera: Camera):
        # For now ONLY SQUARE (ofc I'll add derived particles)
        particle_rect = pygame.Rect(*self.draw_pos, self.size, self.size)
        if not self.static:
            particle_rect = camera.apply(particle_rect)

        pygame.gfxdraw.box(
            screen,
            particle_rect,
            self.color,
        )


class RoundParticle(Particle):
    def draw(self, camera: Camera):
        # For now ONLY SQUARE (ofc I'll add derived particles)
        particle_rect = pygame.Rect(*self.draw_pos, self.size, self.size)
        if not self.static:
            particle_rect = camera.apply(particle_rect)

        pygame.gfxdraw.filled_circle(
            screen,
            particle_rect.centerx, particle_rect.centery,
            self.size,
            self.color,
        )


class ImageParticle(Particle):
    def __init__(self):
        super().__init__()

        self.image = None

    class Builder(Particle.Builder):
        def image(
            self,
            image: pygame.Surface,
            convert_mode: str = "alpha",
            scale: Optional[float] = None,
            colorkey: Optional[Color] = None,
        ):
            if convert_mode == "convert":
                image = image.convert()
            elif convert_mode == "alpha":
                image = image.convert_alpha()
            if scale:
                image = pygame.transform.smoothscale(image, (image.get_width() * scale, image.get_height() * scale))
            if colorkey is not None:
                image.set_colorkey(colorkey)

            self.particle.image = image

            return self

        def effect_fade(self, start_fade_frac: float = 0):
            def fade(particle):
                start_fade = start_fade_frac * particle.lifespan
                if particle.life < start_fade:
                    return

                adj_alpha = (particle.life - start_fade) / (particle.lifespan - start_fade)
                particle.image.set_alpha(max(min(int((1 - adj_alpha) * 255), 255), 0))

            return self._effect(fade)

    # For the typehints
    def builder(self):
        return self.Builder(self)

    def draw(self, camera: Camera):
        if not self.static:
            # It's technically now a rect, but that doesn't matter
            self.draw_pos = camera.apply(self.draw_pos, self.parallax_val)

        screen.blit(self.image, self.draw_pos)


class TextParticle(Particle):
    def __init__(self):
        super().__init__()

        self.text_surf = None

    class Builder(Particle.Builder):
        def text(self, text: str, font_path: Optional[str] = None):
            if font_path is None:
                font = utils.load_font(self.particle.size)
            else:
                font = utils.load_font(self.particle.size, font_path)

            self.particle.text_surf = font.render(text, True, self.particle.color)
            return self

        def effect_easeout_drift(self, easeout_speed: float):
            def easeout_y_drift(particle):
                particle.vel.y *= easeout_speed

            return self._effect(easeout_y_drift)

    # For the typehints
    def builder(self):
        return self.Builder(self)

    def draw(self, camera: Camera):
        self.text_surf.set_alpha(self.color.a)
        screen.blit(self.text_surf, camera.apply(pygame.Rect(*self.draw_pos, self.size, self.size)))


class WindParticle(Particle):
    def update(self):
        super().update()

        # Makes transitions smooth
        self.vel.x += (self.starting_vel.x - self.vel.x) / 20
        self.vel.x += (-2 / 50 + self.starting_vel.x - self.vel.x) / 7
        self.per_frame_vel.x = math.sin(pygame.time.get_ticks() / 1000 * (self.starting_vel.x + 0.5) / 10) * 2
