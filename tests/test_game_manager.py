"""Unit test per game_manager.py"""

# pylint: disable=redefined-outer-name

import json
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

from src.core.game_manager import GameManager
from src.core.modes import ClassicMode, ModeError, TrainingMode
from src.core.word_provider import WordProvider


@pytest.fixture
def mock_word_provider():
    """Fixture per creare un WordProvider mockato."""
    provider = Mock(spec=WordProvider)
    provider.is_valid_word.return_value = True
    return provider


@pytest.fixture
def mock_repo():
    """Fixture per creare un GameRepository mockato."""
    repo = Mock()
    repo.load_game_state.return_value = None
    repo.has_played_today.return_value = False
    repo.get_leaderboard_data.return_value = [("alice", 100), ("bob", 80)]
    return repo


def test_start_game_classic_new(mock_word_provider, mock_repo):
    """Verifica che start_game in modalità classic crei una partita nuova correttamente."""
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "test_user")

    assert isinstance(manager.current_mode, ClassicMode)
    assert manager.language == "it"
    assert manager.current_user == "test_user"
    assert manager.get_attempts() == 0
    assert manager.get_target_word() != ""


def test_start_game_training(mock_word_provider, mock_repo):
    """Verifica che start_game in modalità training crei correttamente la partita."""
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("training", "it")

    assert isinstance(manager.current_mode, TrainingMode)
    assert manager.language == "it"
    assert manager.current_user is None


def test_submit_guess_correct_game_over(mock_word_provider, mock_repo):
    """Verifica che una parola corretta faccia terminare il gioco e salvi il punteggio."""
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    game = manager.current_mode.current_game
    game.target_word = "gatto"
    game.max_attempts = 1

    manager.submit_guess("gatto")

    assert game.is_over
    assert game.won
    assert game.attempts == 1
    assert game.guesses[-1] == "gatto"
    mock_repo.save_score.assert_called_once()
    assert mock_repo.save_game_state.call_count >= 2


def test_submit_guess_wrong_max_attempts(mock_word_provider, mock_repo):
    """Verifica che il gioco termini se si esauriscono i tentativi sbagliando."""
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    game = manager.current_mode.current_game
    game.target_word = "gatto"
    game.max_attempts = 1

    manager.submit_guess("pacco")

    assert game.is_over
    assert not game.won
    assert game.attempts == 1
    assert game.guesses[-1] == "pacco"
    mock_repo.save_score.assert_called_once()


def test_submit_guess_invalid_word_raises(mock_word_provider, mock_repo):
    """Verifica che submit_guess lanci ValueError se la parola non è valida."""
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    mock_word_provider.is_valid_word.return_value = False

    with pytest.raises(ValueError):
        manager.submit_guess("zzzzz")


def test_restore_saved_game(mock_word_provider, mock_repo):
    """Verifica che una partita salvata venga ripristinata correttamente."""
    saved_state = {
        "target_word": "gatto",
        "attempts": 2,
        "guesses": ["pacco", "ratto"],
        "is_over": False,
        "language": "it",
        "mode": "classic",
    }
    mock_repo.load_game_state.return_value = json.dumps(saved_state)

    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    game = manager.current_mode.current_game
    assert game.target_word == "gatto"
    assert game.attempts == 2
    assert game.guesses == ["pacco", "ratto"]
    assert not game.is_over


def test_has_played_classic_today(mock_word_provider, mock_repo):
    """Verifica has_played_classic_today restituisce True se l'utente ha già giocato."""
    manager = GameManager(mock_word_provider, mock_repo)
    mock_repo.has_played_today.return_value = True
    assert manager.has_played_classic_today("user") is True


def test_reset_game(mock_word_provider, mock_repo):
    """Verifica che reset_game azzeri la partita corrente."""
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")
    manager.reset_game()
    assert manager.current_mode is None
    assert manager.get_target_word() == ""


def test_get_leaderboard_success(mock_word_provider, mock_repo):
    """Verifica che la leaderboard venga restituita correttamente."""
    mock_repo.get_leaderboard_data.return_value = [
        {"user": "alice", "score": 100},
        {"user": "bob", "score": 80},
    ]

    manager = GameManager(mock_word_provider, mock_repo)

    result = manager.get_leaderboard()

    assert isinstance(result, list)
    assert result[0]["user"] == "alice"
    assert result[0]["score"] == 100


def test_get_leaderboard_attribute_error(mock_word_provider, mock_repo):
    """Verifica che venga restituita lista vuota se il metodo non esiste."""
    # Simula metodo non implementato
    del mock_repo.get_leaderboard_data

    manager = GameManager(mock_word_provider, mock_repo)

    result = manager.get_leaderboard()

    assert result == []


def test_get_leaderboard_no_repository(mock_word_provider):
    """Verifica che venga restituita lista vuota se il repository è None."""
    manager = GameManager(mock_word_provider, None)

    result = manager.get_leaderboard()

    assert result == []


# =========================
# TEST MIRATI PER LE RIGHE MANCANTI
# =========================


def test_restore_json_error(mock_word_provider, mock_repo):
    """Copre righe 77-78: JSONDecodeError / KeyError durante il restore partita."""
    # Simula JSON malformato
    mock_repo.load_game_state.return_value = "{ invalid json }"
    manager = GameManager(mock_word_provider, mock_repo)
    # Non deve crashare e deve creare comunque la modalità
    manager.start_game("classic", "it", user="user")
    assert manager.current_mode is not None


def test_start_game_already_played_runtime_error(mock_word_provider, mock_repo):
    """Copre righe 98-99: RuntimeError se l'utente ha già giocato oggi."""
    mock_repo.has_played_today.return_value = True
    manager = GameManager(mock_word_provider, mock_repo)
    import pytest

    with pytest.raises(RuntimeError, match="Classic mode already played today"):
        manager.start_game("classic", "it", user="user")


def test_start_game_invalid_mode_raises_modeerror():
    """Copre righe 111-112: raise ModeError se la modalità non è 'classic' né 'training'."""
    mock_wp = MagicMock()
    mock_repo = MagicMock()
    manager = GameManager(mock_wp, mock_repo)

    with pytest.raises(ModeError, match="Invalid mode: invalid_mode"):
        manager.start_game("invalid_mode", "it")


def test_submit_guess_no_active_game_raises():
    """Copre righe 111-112: submit_guess senza partita attiva deve sollevare RuntimeError."""
    gm = GameManager(MagicMock())  # nessun current_mode
    with pytest.raises(RuntimeError, match="No active game"):
        gm.submit_guess("PAROLA")


def test_submit_guess_save_score_exception_runs():
    """Copre righe 188-192: errore nel salvataggio dello score finale, submit_guess non crasha."""
    mock_wp = MagicMock()
    mock_wp.is_valid_word.return_value = True

    mock_repo = MagicMock()
    mock_repo.save_score.side_effect = Exception("DB Error")
    mock_repo.load_game_state.return_value = ""  # evita TypeError
    mock_repo.has_played_today.return_value = (
        False  # permette di partire con classic game
    )

    manager = GameManager(mock_wp, mock_repo)
    manager.start_game("classic", "it", user="user")

    game = manager.current_mode.current_game
    game.target_word = "GATTO"
    game.max_attempts = 1

    result = manager.submit_guess(
        "GATTO"
    )  # termina il gioco → entra nel try/except save_score
    assert isinstance(result, list)
    assert game.is_over


def test_is_game_over_without_game_returns_true():
    """Copre righe 188-192: is_game_over deve ritornare True se non c’è partita o current_game è None."""
    gm = GameManager(MagicMock())

    # current_mode è None → True
    assert gm.is_game_over() is True

    # current_mode c’è ma current_game è None → True
    gm.current_mode = MagicMock()
    gm.current_mode.current_game = None
    assert gm.is_game_over() is True


def test_get_score_training_mode_returns_zero():
    """Copre riga 211: get_score in modalità training deve ritornare 0."""
    mock_wp = MagicMock()
    mock_repo = MagicMock()

    manager = GameManager(mock_wp, mock_repo)
    manager.start_game("training", "it")  # avvia la modalità training

    # get_score deve tornare 0 perché non è ClassicMode
    assert manager.get_score() == 0


def test_get_current_user_returns_user():
    """Copre riga 211: get_current_user ritorna l’utente corrente."""
    gm = GameManager(MagicMock())

    # Nessun utente impostato → None
    assert gm.get_current_user() is None

    # Imposta un utente → ritorna il valore corretto
    gm.current_user = "pippo"
    assert gm.get_current_user() == "pippo"


def test_has_played_classic_today_no_repo(mock_word_provider):
    """Copre riga 232: has_played_classic_today senza repository -> ritorna False."""
    manager = GameManager(mock_word_provider, None)
    assert manager.has_played_classic_today("user") is False
