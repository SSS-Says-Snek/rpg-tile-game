"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the implementation of the Particle system as well as particles.
I decided for particles to NOT be ECS entities.
"""

import random
from math import radians, sin, cos
from typing import Callable, Union

import pygame.gfxdraw
from src import pygame, screen, utils

from src.display.camera import Camera


class ParticleSystem(set):
    def __init__(self, camera: Camera, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = camera

    def update(self) -> None:
        dead_particles = set()

        for particle in self:
            particle.update()

            if not particle.alive:
                dead_particles.add(particle)

        self.difference_update(dead_particles)

    def draw(self):
        for particle in self:
            particle.draw(self.camera)

    def create_hit_particles(self, num_particles, pos, color_list) -> None:
        for _ in range(num_particles):
            self.add(
                Particle()
                .builder()
                .at(pos=pos.pos, angle=random.gauss(180, 180))
                .color(color=random.choice(color_list))
                .gravity(gravity_acc=0.35, gravity_y_vel=-3.5)
                .lifespan(frames=40)
                .speed(speed=random.gauss(1.4, 0.8))
                .effect_fade(start_fade_frac=0.5)
                .build()
            )

    def create_effect_particle(self, color_func, pos, offset: tuple = (0, 0)):
        self.add(
            Particle()
            .builder()
            .at(pygame.Vector2(pos.x + offset[0], pos.y + offset[1]), random.gauss(180, 140))
            .gravity(gravity_acc=0.35, gravity_y_vel=-5)
            .hsv(*color_func())
            .lifespan(frames=40)
            .speed(speed=random.gauss(1.4, 0.8))
            .effect_fade(start_fade_frac=0.5)
            .build()
        )

    def create_fire_particle(self, pos, offset: tuple = (0, 0)):
        self.create_effect_particle(
            lambda: (random.gauss(20, 20), random.gauss(1, 0.1)), pos, offset
        )

    def create_regen_particle(self, pos, offset: tuple = (0, 0)):
        self.create_effect_particle(
            lambda: (random.gauss(120, 20), random.gauss(1, 0.08)), pos, offset
        )

    def create_text_particle(self, pos, txt, color=(0, 0, 0)):
        self.add(
            TextParticle()
            .builder()
            .at(pos=pos)
            .color(color=color)
            .constant_vel(constant_vel=pygame.Vector2(0, -3))
            .lifespan(frames=30)
            .size(size=20)
            .text(text=txt)
            .effect_easeout_drift(easeout_speed=0.93)
            .effect_fade(start_fade_frac=0.5)
            .die_only_lifespan()
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
        self.constant_vel = pygame.Vector2(0, 0)
        self.color = pygame.Color(0, 0, 0, 255)
        self.angle = 0
        self.speed = 0
        self.lifespan = 60
        self.size = 10
        self.gravity = 0

        self.die_only_lifespan = False
        self.alive = True
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

        def constant_vel(self, constant_vel: pygame.Vector2):
            self.particle.constant_vel = constant_vel.copy()
            return self

        def gravity(self, gravity_acc, gravity_y_vel: float = 0):
            self.particle.gravity = gravity_acc
            self.particle.gravity_vel = gravity_y_vel
            return self

        def hsv(self, hue, saturation: float = 1.0, value: float = 1.0):
            h = round(hue) % 360
            s = max(min(round(100 * saturation), 100), 0)
            v = max(min(round(100 * value), 100), 0)
            self.particle.color.hsva = (h, s, v, 100)
            return self

        def lifespan(self, frames: int):
            self.particle.lifespan = frames
            return self

        def size(self, size: float):
            self.particle.size = size
            return self

        def speed(self, speed: float):
            self.particle.speed = speed
            return self

        def die_only_lifespan(self):
            self.particle.die_only_lifespan = True
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

        self.pos += (
            cos(radians(self.angle)) * self.speed,
            sin(radians(self.angle)) * self.speed,
        )
        self.pos += self.constant_vel
        self.pos.y += self.gravity_vel
        self.draw_pos = self.pos.copy()

        if self.life >= self.lifespan:
            if self.die_only_lifespan:
                self.alive = False
            elif self.speed <= 0 or self.size <= 0 or self.color.a == 0:
                self.alive = False

        for effect in self.effects:
            effect(self)

    def draw(self, camera):
        # For now ONLY SQUARE (ofc I'll add derived particles)
        pygame.gfxdraw.box(
            screen,
            camera.apply(pygame.Rect(*self.draw_pos, self.size, self.size)),
            self.color,
        )


class TextParticle(Particle):
    def __init__(self):
        super().__init__()

        self.text_surf = None

    class Builder(Particle.Builder):
        def text(self, text: str, font_path=None):
            if font_path is None:
                font = utils.load_font(self.particle.size)
            else:
                font = utils.load_font(self.particle.size, font_path)

            self.particle.text_surf = font.render(text, True, self.particle.color)
            return self

        def effect_easeout_drift(self, easeout_speed: float):
            def easeout_y_drift(particle):
                particle.constant_vel.y *= easeout_speed

            return self._effect(easeout_y_drift)

    def builder(self):
        return self.Builder(self)

    def draw(self, camera):
        self.text_surf.set_alpha(self.color.a)
        screen.blit(
            self.text_surf, camera.apply(pygame.Rect(*self.draw_pos, self.size, self.size))
        )
