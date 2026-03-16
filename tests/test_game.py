"""" Unit test per game.py"""

import pytest
from src.core.game import Game


def test_game_initialization():
    game = Game("APPLE")

    assert game.target_word == "APPLE"
    assert game.attempts == 0
    assert game.is_over is False
    assert game.max_attempts == 6