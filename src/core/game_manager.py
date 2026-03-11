"""Game manager coordina le sessioni di gioco."""

import logging
from typing import Optional, List

from .game import Game
from .word_provider import WordProvider
from .modes import ClassicMode, TrainingMode, ModeError


logger = logging.getLogger(__name__)


class GameManager:
    """
    Coordina il gioco, scegliendo la modalità e collegando
    le chiamate della UI alla logica del gioco.
    """

    def __init__(self, word_provider: WordProvider) -> None:
        """
        Inizializzazione

        Args:
            word_provider: Recupera le parole.
        """
        self.word_provider: WordProvider = word_provider
        self.current_mode: Optional[ClassicMode | TrainingMode] = None
        self.language: Optional[str] = None
        self.word_length: Optional[int] = None
    def start_game(self, mode: str, language: str, word_length: int) -> None:
        """
        Inizia un nuovo gioco nella modalità scelta

        Args:
            mode: "classic" or "training".
            language: Language code (e.g., "it", "en").
            word_length: Desired word length.

        Raises:
            ModeError: If mode is invalid or game cannot be started.
        """
        self.language = language
        self.word_length = word_length

        if mode == "classic":
            self.current_mode = ClassicMode(self.word_provider)
        elif mode == "training":
            self.current_mode = TrainingMode(self.word_provider)
        else:
            logger.error("Invalid mode requested: %s", mode)
            raise ModeError(f"Invalid mode: {mode}")

        try:
            self.current_mode.start_game(language, word_length)
            logger.info(
                "Game started | mode=%s language=%s length=%s",
                mode,
                language,
                word_length,
            )
        except ModeError as exc:
            logger.error("Failed to start game: %s", exc)
            raise

    def submit_guess(self, guess: str) -> List[str]:
        """
        Submit a guess to the current game.

        Args:
            guess: Word guessed by the player.

        Returns:
            List of results for each letter: "Corretto", "Presente", or "Assente".

        Raises:
            RuntimeError: If no game is active.
        """
        if self.current_mode is None:
            logger.error("Attempted guess without active game.")
            raise RuntimeError("No active game")

        result = self.current_mode.submit_guess(guess)
        logger.info("Guess submitted: %s | result=%s", guess, result)
        return result

    def is_game_over(self) -> bool:
        """
        Check if the current game is over.

        Returns:
            True if the game has ended, False otherwise.
        """
        if self.current_mode is None:
            return True

        if isinstance(self.current_mode, ClassicMode):
            game = self.current_mode.current_game
        else:
            game = self.current_mode.current_game

        return game.is_over if game else True

    def get_attempts(self) -> int:
        """
        Return the number of attempts made in the current game.

        Returns:
            Number of attempts.

        Raises:
            RuntimeError: If no game is active.
        """
        if self.current_mode is None:
            logger.error("Attempts requested without active game.")
            raise RuntimeError("No active game")

        game: Optional[Game] = self.current_mode.current_game
        if game is None:
            return 0

        return game.attempts
    def get_score(self) -> int:
        """
        Restituisce il punteggio per la modalità classica.

        """
        if isinstance(self.current_mode, ClassicMode):
            return self.current_mode.score
        return 0

    def reset_game(self) -> None:
        """Resetta la sessione di gioco corrente."""
        logger.info("Resetting game session.")
        self.current_mode = None