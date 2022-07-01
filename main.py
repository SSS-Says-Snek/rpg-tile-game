"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file is used to run the actual game
"""

from __future__ import annotations

from src.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
