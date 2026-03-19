""" " Unit test per game.py"""

import pytest
from src.core.game import Game


def test_game_initialization():
    """Verifica che il gioco venga inizializzato correttamente."""
    game = Game("APPLE")

    assert game.target_word == "APPLE"
    assert game.attempts == 0
    assert game.is_over is False
    assert game.max_attempts == 6


def test_correct_guess():
    """Verifica che una parola indovinata restituisca tutti 'Corretto'
    e termini la partita."""
    game = Game("APPLE")

    result = game.check_guess("APPLE")

    assert result == ["Corretto", "Corretto", "Corretto", "Corretto", "Corretto"]
    assert game.is_over is True
    assert game.attempts == 1


def test_letter_present():
    """Verifica per lettera presente"""
    game = Game("APPLE")

    result = game.check_guess("PLANE")

    assert "Presente" in result


def test_letter_absent():
    """Verifica per lettere non presenti."""
    game = Game("APPLE")

    result = game.check_guess("ZZZZZ")

    assert result == ["Assente", "Assente", "Assente", "Assente", "Assente"]


def test_attempt_counter():
    """Verifica che il numero di tentativi venga incrementato
    correttamente dopo ogni guess."""
    game = Game("APPLE")

    game.check_guess("AAAAA")
    game.check_guess("BBBBB")

    assert game.attempts == 2


def test_invalid_length():
    """ "Verifica per la lunghezza della parola"""
    game = Game("APPLE")

    with pytest.raises(ValueError):
        game.check_guess("ABC")


def test_game_over_after_win():
    """Verifica che non sia possibile fare altri tentativi
    dopo aver indovinato la parola."""
    game = Game("APPLE")

    game.check_guess("APPLE")

    with pytest.raises(RuntimeError):
        game.check_guess("APPLE")


def test_game_over_after_max_attempts():
    """Verifica che il gioco termini dopo aver raggiunto
    il numero massimo di tentativi."""
    game = Game("APPLE", max_attempts=2)

    game.check_guess("AAAAA")
    game.check_guess("BBBBB")

    assert game.is_over is True


def test_guess_after_game_over():
    """Verifica che venga sollevato RuntimeError se si prova
    a indovinare dopo che il gioco è terminato."""
    game = Game("APPLE", max_attempts=1)

    game.check_guess("AAAAA")

    with pytest.raises(RuntimeError):
        game.check_guess("BBBBB")


def test_win_before_max_attempts():
    """Verifica che il gioco termini correttamente
    quando la parola viene indovinata prima dei tentativi massimi."""
    game = Game("APPLE")

    game.check_guess("AAAAA")
    result = game.check_guess("APPLE")

    assert result == ["Corretto"] * 5
    assert game.is_over
    assert game.attempts == 2
