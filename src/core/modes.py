"""Game modes module for Wordle."""

import logging
from typing import List, Optional

from src.core.game import Game
from src.core.word_provider import WordProvider

logger = logging.getLogger(__name__)


class ModeError(Exception):
    """Custom exception per errori nelle modalità."""

 
class ClassicMode:
    """Modalità classica (parola del giorno)."""

    def __init__(self, word_provider: WordProvider) -> None:
        self.word_provider: WordProvider = word_provider
        self.current_game: Optional[Game] = None
        self.score: int = 0

    def start_game(self, language: str) -> None:
        """
        Avvia una nuova partita in modalità classica.

        Recupera la parola del giorno tramite il WordProvider e inizializza
        una nuova istanza di Game. La parola sarà identica per tutti i
        giocatori nella stessa giornata.
        """
        word = self.word_provider.get_daily_word(language)
        self.current_game = Game(word)
        logger.info(
            "Classic mode game started | language=%s",
            language
        )

    def submit_guess(self, guess: str) -> List[str]:
        """
        Invia un tentativo alla partita in corso.

        Il tentativo viene controllato dal Game e viene restituito il
        risultato per ogni lettera.

        Se il giocatore indovina la parola, il punteggio della modalità
        classica viene incrementato.
        """
        if self.current_game is None:
            logger.error("Attempted guess without active classic game.")
            raise ModeError("No active game")

        result = self.current_game.check_guess(guess)

        if guess == self.current_game.target_word:
            self.score += 1
            logger.info("Correct guess! Score incremented to %d.", self.score)

        return result


class TrainingMode:
    """Modalità allenamento"""

    def __init__(self, word_provider: WordProvider) -> None:
        self.word_provider: WordProvider = word_provider
        self.current_game: Optional[Game] = None

    def start_game(self, language: str) -> None:
        """Avvia una nuova partita in modalità allenamento."""
        word = self.word_provider.get_random_word(language)
        self.current_game = Game(word)
        logger.info(
            "Training mode game started | language=%s",
            language
        )
        
    def submit_guess(self, guess: str) -> List[str]:
        """Invia un tentativo alla partita di allenamento."""
        if self.current_game is None:
            logger.error("Attempted guess without active training game.")
            raise ModeError("No active game")

        result = self.current_game.check_guess(guess)
        return result
