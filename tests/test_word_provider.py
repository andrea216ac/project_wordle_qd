"""tests/test_word_provider.py"""

import datetime
from unittest.mock import Mock

import pytest

from src.core.word_provider import WordProvider


class FakeWord:  # pylint: disable=too-few-public-methods
    """Classe finta per simulare l'oggetto restituito da WordRepository."""

    def __init__(self, word):
        self.word = word


def test_get_random_word_success():
    """Testa che get_random_word restituisca correttamente la parola dal repository."""
    # Creiamo un mock di WordRepository che restituisce un oggetto FakeWord
    mock_repo = Mock()
    mock_repo.get_random_word.return_value = FakeWord("ciao")

    provider = WordProvider(mock_repo)
    result = provider.get_random_word("it")

    # Verifica che la parola restituita sia quella corretta
    assert result == "ciao"
    # Verifica che il metodo del repository sia stato chiamato con i parametri giusti
    mock_repo.get_random_word.assert_called_once_with("it", 5)


def test_get_random_word_none():
    """Testa che get_random_word sollevi ValueError se non ci sono parole disponibili."""
    mock_repo = Mock()
    mock_repo.get_random_word.return_value = None

    provider = WordProvider(mock_repo)
    # Controlla che venga sollevata l'eccezione corretta
    with pytest.raises(ValueError, match="Language not available"):
        provider.get_random_word("it")


def test_get_daily_word_success():
    """Testa che get_daily_word restituisca correttamente la parola del giorno."""
    today = datetime.date.today()
    mock_repo = Mock()
    mock_repo.get_daily_word.return_value = FakeWord("parola")

    provider = WordProvider(mock_repo)
    result = provider.get_daily_word("it")

    # Verifica che la parola restituita sia quella corretta
    assert result == "parola"
    # Verifica che il metodo del repository sia stato chiamato con data e parametri giusti
    mock_repo.get_daily_word.assert_called_once_with(today, "it", 5)


def test_get_daily_word_none():
    """Testa che get_daily_word sollevi ValueError se non esiste una parola del giorno."""
    mock_repo = Mock()
    mock_repo.get_daily_word.return_value = None

    provider = WordProvider(mock_repo)
    # Controlla che venga sollevata l'eccezione corretta
    with pytest.raises(ValueError, match="No word available"):
        provider.get_daily_word("it")
