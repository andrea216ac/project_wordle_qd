"""" Unit test per game.py"""

import pytest
from src.core.game import Game


def test_game_initialization():
    game = Game("APPLE")

    assert game.target_word == "APPLE"
    assert game.attempts == 0
    assert game.is_over is False
    assert game.max_attempts == 6

def test_correct_guess():
    game = Game("APPLE")

    result = game.check_guess("APPLE")

    assert result == ["Corretto", "Corretto", "Corretto", "Corretto", "Corretto"]
    assert game.is_over is True
    assert game.attempts == 1

def test_letter_present():
    game = Game("APPLE")

    result = game.check_guess("PLANE")

    assert "Presente" in result


def test_letter_absent():
    game = Game("APPLE")

    result = game.check_guess("ZZZZZ")

    assert result == ["Assente", "Assente", "Assente", "Assente", "Assente"]


def test_attempt_counter():
    game = Game("APPLE")

    game.check_guess("AAAAA")
    game.check_guess("BBBBB")

    assert game.attempts == 2


def test_invalid_length():
    game = Game("APPLE")

    with pytest.raises(ValueError):
        game.check_guess("ABC")


def test_game_over_after_win():
    game = Game("APPLE")

    game.check_guess("APPLE")

    with pytest.raises(RuntimeError):
        game.check_guess("APPLE")


def test_game_over_after_max_attempts():
    game = Game("APPLE", max_attempts=2)

    game.check_guess("AAAAA")
    game.check_guess("BBBBB")

    assert game.is_over is True


def test_guess_after_game_over():
    game = Game("APPLE", max_attempts=1)

    game.check_guess("AAAAA")

    with pytest.raises(RuntimeError):
        game.check_guess("BBBBB")

def test_win_before_max_attempts():
    game = Game("APPLE")

    game.check_guess("AAAAA")
    result = game.check_guess("APPLE")

    assert result == ["Corretto"] * 5
    assert game.is_over
    assert game.attempts == 2