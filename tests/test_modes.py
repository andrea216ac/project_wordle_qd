"""Unit test per modes.py."""

import pytest

from src.core.modes import ClassicMode, ModeError, TrainingMode


class FakeWordProvider:
    """WordProvider finto per i test."""

    def get_daily_word(self, language):
        """Restituisce sempre la stessa parola per i test."""
        return "APPLE"

    def get_random_word(self, language):
        """Restituisce sempre la stessa parola per i test."""
        return "TRAIN"


def test_classic_mode_start_game():
    """Verifica che ClassicMode avvii correttamente una partita."""
    provider = FakeWordProvider()
    mode = ClassicMode(provider)

    mode.start_game("it")

    assert mode.current_game is not None
    assert mode.current_game.target_word == "APPLE"


def test_classic_mode_submit_guess():
    """Verifica che submit_guess restituisca il risultato del Game."""
    provider = FakeWordProvider()
    mode = ClassicMode(provider)

    mode.start_game("it")

    result = mode.submit_guess("APPLE")

    assert result == ["Corretto"] * 5


def test_classic_mode_score_increment():
    """Verifica che il punteggio aumenti quando la parola è indovinata."""
    provider = FakeWordProvider()
    mode = ClassicMode(provider)

    mode.start_game("it")

    mode.submit_guess("APPLE")

    assert mode.score == 1


def test_classic_mode_no_active_game():
    """Verifica che venga sollevato ModeError se non esiste una partita attiva."""
    provider = FakeWordProvider()
    mode = ClassicMode(provider)

    with pytest.raises(ModeError):
        mode.submit_guess("APPLE")


def test_training_mode_start_game():
    """Verifica che TrainingMode avvii correttamente una partita."""
    provider = FakeWordProvider()
    mode = TrainingMode(provider)

    mode.start_game("it")

    assert mode.current_game is not None
    assert mode.current_game.target_word == "TRAIN"


def test_training_mode_submit_guess():
    """Verifica che submit_guess funzioni correttamente in TrainingMode."""
    provider = FakeWordProvider()
    mode = TrainingMode(provider)

    mode.start_game("it")

    result = mode.submit_guess("TRAIN")

    assert result == ["Corretto"] * 5


def test_training_mode_no_active_game():
    """Verifica che venga sollevato ModeError se si tenta un guess senza partita."""
    provider = FakeWordProvider()
    mode = TrainingMode(provider)

    with pytest.raises(ModeError):
        mode.submit_guess("TRAIN")
