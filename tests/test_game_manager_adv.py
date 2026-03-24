"""Test definitivi per il sorpasso: GameManager al 100%."""

import json
from unittest.mock import MagicMock, patch
import pytest
from src.core.game_manager import GameManager

class TestGameManagerAdvanced:
    """Suite per coprire le ultime righe della logica di business."""

    def test_start_game_classic_already_played(self):
        """Testa il blocco se l'utente ha già giocato oggi."""
        mock_wp = MagicMock()
        mock_repo = MagicMock()
        mock_repo.load_game_state.return_value = ""
        mock_repo.has_played_today.return_value = True
        
        gm = GameManager(mock_wp, score_repository=mock_repo)
        
        with pytest.raises(RuntimeError, match="Classic mode already played today"):
            gm.start_game("classic", "IT", user="Angelo")

    def test_restore_saved_game_success(self):
        """Testa il ripristino completo di una partita da JSON."""
        mock_wp = MagicMock()
        mock_repo = MagicMock()
        state = {
            "mode": "classic",
            "language": "IT",
            "target_word": "GATTO",
            "attempts": 2,
            "guesses": ["CANE", "TOPO"],
            "is_over": False
        }
        mock_repo.load_game_state.return_value = json.dumps(state)
        
        gm = GameManager(mock_wp, score_repository=mock_repo)
        gm.start_game("classic", "IT", user="Angelo")
        
        assert gm.current_mode is not None
        assert gm.get_target_word() == "GATTO"

    def test_submit_guess_invalid_word(self):
        """Testa la reazione a una parola non valida."""
        mock_wp = MagicMock()
        mock_wp.is_valid_word.return_value = False
        
        gm = GameManager(mock_wp)
        gm.start_game("training", "IT")
        
        with pytest.raises(ValueError, match="Questa parola non esiste"):
            gm.submit_guess("XXXXX")

    def test_submit_guess_save_state_error(self):
        """Testa la gestione errori nel salvataggio stato."""
        mock_wp = MagicMock()
        mock_wp.is_valid_word.return_value = True
        
        mock_repo = MagicMock()
        mock_repo.save_game_state.side_effect = Exception("DB Error")
        
        gm = GameManager(mock_wp, score_repository=mock_repo)
        gm.start_game("training", "IT", user="Angelo")
        
        # Forza la parola target per evitare l'errore di lunghezza
        gm.current_mode.current_game.target_word = "GATTO"
        
        res = gm.submit_guess("GATTO")
        assert isinstance(res, list)

    def test_get_leaderboard_exception(self):
        """Testa l'eccezione se il repository non ha il metodo."""
        mock_repo = MagicMock()
        del mock_repo.get_leaderboard_data
        
        gm = GameManager(MagicMock(), score_repository=mock_repo)
        assert gm.get_leaderboard() == []

    def test_get_attempts_error(self):
        """Copre la riga dell'errore se si chiedono tentativi senza gioco attivo."""
        gm = GameManager(MagicMock())
        with pytest.raises(RuntimeError, match="No active game"):
            gm.get_attempts()