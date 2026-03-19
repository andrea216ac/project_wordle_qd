"""Unit test per game_manager.py."""

from unittest.mock import Mock

import pytest

from src.core.game_manager import GameManager
from src.core.modes import ModeError


class FakeWordProvider:  # pylint: disable=too-few-public-methods
    """Provider finto per evitare dipendenze reali."""

    def get_daily_word(self, _: str) -> str:
        """Restituisce sempre una parola fissa per la modalità classica."""
        return "cane"

    def get_random_word(self, _: str) -> str:
        """Restituisce sempre una parola fissa per la modalità training."""
        return "gatto"


class FakeGame:  # pylint: disable=too-few-public-methods
    """Game finto per simulare stato della partita."""

    def __init__(self, is_over=False, attempts=1):
        self.is_over = is_over
        self.attempts = attempts


class FakeMode:  # pylint: disable=too-few-public-methods
    """Modalità finta per simulare Classic/Training."""

    def __init__(self):
        self.current_game = FakeGame()
        self.score = 0

    def start_game(self, _: str):
        """Simula avvio partita."""
        self.current_game = FakeGame()

    def submit_guess(self, _: str):
        """Simula invio guess."""
        return ["Corretto"] * 5


# ========================
# TEST START GAME
# ========================


def test_start_game_classic_success():
    """Verifica che start_game inizializzi correttamente la modalità classica."""
    provider = FakeWordProvider()
    manager = GameManager(provider)

    manager.start_game("classic", "it", user="test_user")

    assert manager.current_mode is not None
    assert manager.language == "it"
    assert manager.current_user == "test_user"


def test_start_game_training_success():
    """Verifica che start_game inizializzi correttamente la modalità training."""
    provider = FakeWordProvider()
    manager = GameManager(provider)

    manager.start_game("training", "it")

    assert manager.current_mode is not None


def test_start_game_invalid_mode():
    """Verifica che venga sollevato ModeError per modalità non valida."""
    provider = FakeWordProvider()
    manager = GameManager(provider)

    with pytest.raises(ModeError):
        manager.start_game("invalid", "it")


def test_start_game_classic_already_played():
    """Verifica che venga bloccata la modalità classica se l'utente ha già giocato."""
    provider = FakeWordProvider()
    mock_repo = Mock()
    mock_repo.has_played_today.return_value = True

    manager = GameManager(provider, score_repository=mock_repo)

    with pytest.raises(RuntimeError):
        manager.start_game("classic", "it", user="test_user")


# ========================
# TEST SUBMIT GUESS
# ========================


def test_submit_guess_success():
    """Verifica che submit_guess ritorni il risultato correttamente."""
    provider = FakeWordProvider()
    manager = GameManager(provider)

    manager.current_mode = FakeMode()

    result = manager.submit_guess("APPLE")

    assert result == ["Corretto"] * 5


def test_submit_guess_no_active_game():
    """Verifica che venga sollevato errore se non esiste una partita attiva."""
    provider = FakeWordProvider()
    manager = GameManager(provider)

    with pytest.raises(RuntimeError):
        manager.submit_guess("APPLE")


def test_submit_guess_game_over_saves_score():
    """Verifica che il punteggio venga salvato quando il gioco termina."""
    provider = FakeWordProvider()
    mock_repo = Mock()

    manager = GameManager(provider, score_repository=mock_repo)
    manager.current_user = "test_user"

    mode = FakeMode()
    mode.current_game = FakeGame(is_over=True, attempts=3)
    manager.current_mode = mode

    manager.submit_guess("APPLE")

    mock_repo.save_score.assert_called_once_with(
        user="test_user",
        score=0,
        attempts=3,
    )


def test_submit_guess_save_score_exception():
    """Verifica che errori nel salvataggio del punteggio non blocchino il gioco."""
    provider = FakeWordProvider()
    mock_repo = Mock()
    mock_repo.save_score.side_effect = Exception("DB error")

    manager = GameManager(provider, score_repository=mock_repo)
    manager.current_user = "test_user"

    mode = FakeMode()
    mode.current_game = FakeGame(is_over=True, attempts=2)
    manager.current_mode = mode

    # Non deve sollevare eccezioni
    result = manager.submit_guess("APPLE")

    assert result == ["Corretto"] * 5


# ========================
# TEST METODI DI SUPPORTO
# ========================


def test_is_game_over_true():
    """Verifica che is_game_over ritorni True quando il gioco è finito."""
    provider = FakeWordProvider()
    manager = GameManager(provider)

    mode = FakeMode()
    mode.current_game = FakeGame(is_over=True)
    manager.current_mode = mode

    assert manager.is_game_over() is True


def test_is_game_over_no_mode():
    """Verifica che ritorni True se non c'è una partita."""

    provider = FakeWordProvider()
    manager = GameManager(provider)

    assert manager.is_game_over() is True


def test_get_attempts_success():
    """Verifica che get_attempts ritorni il numero corretto di tentativi."""
    manager = GameManager(FakeWordProvider())

    mode = FakeMode()
    mode.current_game = FakeGame(attempts=4)
    manager.current_mode = mode

    assert manager.get_attempts() == 4


def test_get_attempts_no_game():
    """Verifica errore se si richiedono tentativi senza partita."""

    provider = FakeWordProvider()
    manager = GameManager(provider)

    with pytest.raises(RuntimeError):
        manager.get_attempts()


def test_get_score_classic():
    """Verifica che get_score ritorni il punteggio per modalità classica."""
    manager = GameManager(FakeWordProvider())

    mode = FakeMode()
    mode.score = 5
    manager.current_mode = mode

    assert manager.get_score() == 0  # perché FakeMode non è ClassicMode


def test_get_current_user():
    """Verifica che venga restituito l'utente corrente."""
    manager = GameManager(FakeWordProvider())
    manager.current_user = "test_user"

    assert manager.get_current_user() == "test_user"


def test_reset_game():
    """Verifica che reset_game azzeri la modalità corrente."""
    manager = GameManager(FakeWordProvider())
    manager.current_mode = FakeMode()

    manager.reset_game()

    assert manager.current_mode is None


def test_save_score_called_on_game_end():
    """Verifica che save_score venga chiamato quando il gioco termina."""

    provider = FakeWordProvider()

    # Mock del repository
    mock_repo = Mock()
    mock_repo.has_played_today.return_value = False

    manager = GameManager(provider, score_repository=mock_repo)

    manager.start_game("classic", "it", user="test_user")

    # Indovina subito la parola → fine gioco
    manager.submit_guess("cane")

    # Verifica che save_score sia stato chiamato
    mock_repo.save_score.assert_called_once_with(
        user="test_user",
        score=1,
        attempts=1,
    )


def test_save_score_failure_handled():
    """Verifica che un errore in save_score non interrompa il gioco."""

    provider = FakeWordProvider()

    mock_repo = Mock()
    mock_repo.has_played_today.return_value = False

    # Simula errore nel database
    mock_repo.save_score.side_effect = Exception("DB error")

    manager = GameManager(provider, score_repository=mock_repo)

    manager.start_game("classic", "it", user="test_user")

    # Non deve crashare anche se save_score fallisce
    result = manager.submit_guess("cane")

    assert result is not None


# -------------------------
# TEST VALIDAZIONE PAROLA
# -------------------------
def test_submit_guess_invalid_word():
    """Verifica che una parola non valida venga rifiutata."""
    provider = Mock()
    provider.is_valid_word.return_value = False

    manager = GameManager(provider)
    manager.current_mode = FakeMode()
    manager.language = "it"

    with pytest.raises(ValueError):
        manager.submit_guess("xxxxx")


# -------------------------
# TEST SALVATAGGIO STATO
# -------------------------
def test_submit_guess_saves_game_state():
    """Verifica che lo stato della partita venga salvato dopo un tentativo."""
    provider = Mock()
    provider.is_valid_word.return_value = True

    repo = Mock()

    manager = GameManager(provider, repo)
    manager.current_mode = FakeMode()
    manager.language = "it"
    manager.current_user = "test_user"

    manager.submit_guess("cane")

    assert repo.save_game_state.called


# -------------------------
# TEST CONTENUTO SALVATAGGIO
# -------------------------
def test_save_game_state_data():
    """Verifica che i dati salvati siano corretti."""
    provider = Mock()
    provider.is_valid_word.return_value = True

    repo = Mock()

    manager = GameManager(provider, repo)
    manager.current_mode = FakeMode()
    manager.language = "it"
    manager.current_user = "test_user"

    manager.submit_guess("cane")

    args = repo.save_game_state.call_args.kwargs

    assert args["user"] == "test_user"
    assert args["word"] == "cane"
    assert args["attempts"] == 1
    assert args["is_over"] is True


# -------------------------
# TEST NO ACTIVE GAME
# -------------------------
def test_submit_guess_no_game():
    """Verifica errore se non c'è una partita attiva."""
    provider = Mock()
    manager = GameManager(provider)

    with pytest.raises(RuntimeError):
        manager.submit_guess("cane")
