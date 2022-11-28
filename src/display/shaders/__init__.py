"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import struct

import moderngl
import pygame

from src.common import RES, SHADER_DIR, screen


class ShaderManager:
    def __init__(self):
        self.ctx = moderngl.create_context()
        self.program = self.ctx.program(
            vertex_shader=self.load_shader("vertex"), fragment_shader=self.load_shader("fragment")
        )

        # Coordinates to map world coordinates with UV-space
        texture_coordinates = [0, 1, 1, 1, 0, 0, 1, 0]
        world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]

        # Describes triangles to render
        render_indices = [0, 1, 2, 1, 2, 3]

        self.screen_texture = self.ctx.texture(RES, 3, pygame.image.tostring(screen, "RGB", True))
        self.screen_texture.repeat_x = False
        self.screen_texture.repeat_y = False

        vbo = self.load_buffer(world_coordinates, "8f")
        uv_map = self.load_buffer(texture_coordinates, "8f")
        ibo = self.load_buffer(render_indices, "6i")

        vao_content = [(vbo, "2f", "vert"), (uv_map, "2f", "in_text")]
        self.vao = self.ctx.vertex_array(self.program, vao_content, ibo)

    @staticmethod
    def load_shader(name: str):
        with open(SHADER_DIR / f"{name}.glsl") as f:
            return f.read()

    def load_buffer(self, data: list[int], fmt: str):
        return self.ctx.buffer(struct.pack(fmt, *data))

    def render(self):
        texture_data = screen.get_view("1")
        self.screen_texture.write(texture_data)
        self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
        self.screen_texture.use()
        self.vao.render()
        pygame.display.flip()
