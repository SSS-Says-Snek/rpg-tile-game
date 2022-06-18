"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains the implementation of the Particle system as well as particles.
I decided for particles to NOT be ECS entities.
"""

from math import radians, sin, cos

import pygame.gfxdraw
from src import pygame, screen

class ParticleSystem(set):
    def __init__(self, camera, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = camera

    def update(self):
        dead_particles = set()

        for particle in self:
            particle.update()

            if not particle.alive:
                dead_particles.add(particle)

        self.difference_update(dead_particles)

    def draw(self):
        for particle in self:
            particle.draw(self.camera)


class Particle:
    """
    Arguments are NOT passed to particles via instantiation.
    Instead, there is a builder
    """
    def __init__(self):
        # Default values
        self.pos = pygame.Vector2(0, 0)
        self.constant_vel = pygame.Vector2(0, 0)
        self.color = pygame.Color(0)
        self.angle = 0
        self.speed = 3
        self.lifespan = 60
        self.size = 10
        self.gravity = 0

        self.alive = True
        self.life = 0
        self.gravity_vel = 0
        self.effects = set()

    class Builder:
        def __init__(self, particle):
            self.particle = particle

        # ATTRIBUTE SETTERS

        def at(self, pos, angle=0):
            self.particle.pos = pos.copy()
            self.particle.angle = angle
            return self

        def color(self, color):
            self.particle.color = pygame.Color(color)
            return self

        def constant_vel(self, constant_vel):
            self.particle.constant_vel = constant_vel.copy()
            return self

        def gravity(self, gravity_acc, gravity_y_vel=0):
            self.particle.gravity = gravity_acc
            self.particle.gravity_vel = gravity_y_vel
            return self

        def lifespan(self, frames):
            self.particle.lifespan = frames
            return self

        def size(self, size):
            self.particle.size = size
            return self

        def speed(self, speed):
            self.particle.speed = speed
            return self

        # CUSTOM EFFECTS

        def _effect(self, effect):
            self.particle.effects.add(effect)
            return self

        def effect_fade(self, start_fade_frac=0):
            def fade(particle):
                start_fade = start_fade_frac * particle.lifespan
                if particle.life < start_fade:
                    return

                adj_alpha = (particle.life - start_fade) / (particle.lifespan - start_fade)
                particle.color.a = int((1 - adj_alpha) * 255)

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
            sin(radians(self.angle)) * self.speed
        )
        self.pos += self.constant_vel
        self.pos.y += self.gravity_vel

        if self.speed <= 0 or self.size <= 0 or self.life >= self.lifespan or self.color.a == 0:
            self.alive = False

        for effect in self.effects:
            effect(self)

    def draw(self, camera):
        # For now ONLY SQUARE (ofc I'll add derived particles)
        pygame.gfxdraw.box(
            screen, camera.apply(pygame.Rect(*self.pos, self.size, self.size)), self.color
        )
