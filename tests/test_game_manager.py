""" " Unit test per game_manager.py"""

import json
from unittest.mock import Mock

import pytest
from src.core.game_manager import GameManager
from src.core.modes import ClassicMode, TrainingMode
from src.core.word_provider import WordProvider


@pytest.fixture
def mock_word_provider():
    provider = Mock(spec=WordProvider)
    provider.is_valid_word.return_value = True
    return provider


@pytest.fixture
def mock_repo():
    repo = Mock()
    repo.load_game_state.return_value = None
    repo.has_played_today.return_value = False
    repo.get_leaderboard_data.return_value = [("alice", 100), ("bob", 80)]
    return repo


def test_start_game_classic_new(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "test_user")

    assert isinstance(manager.current_mode, ClassicMode)
    assert manager.language == "it"
    assert manager.current_user == "test_user"
    assert manager.get_attempts() == 0
    assert manager.get_target_word() != ""


def test_start_game_training(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("training", "it")

    assert isinstance(manager.current_mode, TrainingMode)
    assert manager.language == "it"
    assert manager.current_user is None


def test_submit_guess_correct_game_over(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    game = manager.current_mode.current_game
    game.target_word = "cane"
    game.max_attempts = 1

    # invio guess corretto → game over
    manager.submit_guess("cane")

    assert game.is_over
    assert game.won
    assert game.attempts == 1
    assert game.guesses[-1] == "cane"
    mock_repo.save_score.assert_called_once()
    assert mock_repo.save_game_state.call_count >= 2


def test_submit_guess_wrong_max_attempts(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    game = manager.current_mode.current_game
    game.target_word = "cane"
    game.max_attempts = 1

    # invio guess sbagliato → game over per tentativi
    manager.submit_guess("pane")

    assert game.is_over
    assert not game.won
    assert game.attempts == 1
    assert game.guesses[-1] == "pane"
    mock_repo.save_score.assert_called_once()


def test_submit_guess_invalid_word_raises(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    mock_word_provider.is_valid_word.return_value = False

    with pytest.raises(ValueError):
        manager.submit_guess("zzzzz")


def test_restore_saved_game(mock_word_provider, mock_repo):
    saved_state = {
        "target_word": "cane",
        "attempts": 2,
        "guesses": ["pane", "lane"],
        "is_over": False,
        "language": "it",
        "mode": "classic",
    }
    mock_repo.load_game_state.return_value = json.dumps(saved_state)

    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")

    game = manager.current_mode.current_game
    assert game.target_word == "cane"
    assert game.attempts == 2
    assert game.guesses == ["pane", "lane"]
    assert not game.is_over


def test_has_played_classic_today(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    mock_repo.has_played_today.return_value = True
    assert manager.has_played_classic_today("user") is True


def test_leaderboard_conversion(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    leaderboard = manager.get_leaderboard()

    assert isinstance(leaderboard, list)
    assert all(isinstance(item, dict) for item in leaderboard)
    assert leaderboard[0]["user"] == "alice"
    assert leaderboard[0]["score"] == 100


def test_reset_game(mock_word_provider, mock_repo):
    manager = GameManager(mock_word_provider, mock_repo)
    manager.start_game("classic", "it", "user")
    manager.reset_game()
    assert manager.current_mode is None
    assert manager.get_target_word() == ""
