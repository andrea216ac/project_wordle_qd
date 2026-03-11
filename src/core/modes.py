"""Game modes module for Wordle."""

import logging
from typing import Optional, List

from .game import Game
from .word_provider import WordProvider


logger = logging.getLogger(__name__)


class ModeError(Exception):
    """Custom exception for game mode errors."""
    pass


class ClassicMode:
    """Handles daily word mode with score tracking."""

    def __init__(self, word_provider: WordProvider) -> None:
        """
        Initialize classic mode.

        Args:
            word_provider: Provider used to retrieve words.
        """
        self.word_provider: WordProvider = word_provider
        self.current_game: Optional[Game] = None
        self.language: Optional[str] = None
        self.word_length: Optional[int] = None
        self.score: int = 0

    def start_game(self, language: str, word_length: int) -> None:
        """
        Start a new daily word game.

        Args:
            language: Language code (e.g. "it", "en").
            word_length: Desired word length.

        Raises:
            ModeError: If starting the game fails.
        """
        self.language = language
        self.word_length = word_length

        try:
            word = self.word_provider.get_daily_word(language, word_length)
            self.current_game = Game(word)
            logger.info(
                "Classic mode game started | language=%s length=%s", language, word_length
            )
        except Exception as exc:
            logger.error("Failed to start classic mode game: %s", exc)
            raise ModeError("Cannot start classic mode") from exc

    def submit_guess(self, guess: str) -> List[str]:
        """
        Submit a guess and update score if correct.

        Args:
            guess: Word guessed by the player.

        Returns:
            Result of the guess evaluation.

        Raises:
            ModeError: If no game is active.
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
    """Handles infinite training games with random words."""

    def __init__(self, word_provider: WordProvider) -> None:
        """
        Initialize training mode.

        Args:
            word_provider: Provider used to retrieve words.
        """
        self.word_provider: WordProvider = word_provider
        self.current_game: Optional[Game] = None
        self.language: Optional[str] = None
        self.word_length: Optional[int] = None

    def start_game(self, language: str, word_length: int) -> None:
        """
        Start a new random word game.

        Args:
            language: Language code.
            word_length: Desired word length.

        Raises:
            ModeError: If starting the game fails.
        """
        self.language = language
        self.word_length = word_length

        try:
            word = self.word_provider.get_random_word(language, word_length)
            self.current_game = Game(word)
            logger.info(
                "Training mode game started | language=%s length=%s",
                language,
                word_length,
            )
        except Exception as exc:
            logger.error("Failed to start training mode game: %s", exc)
            raise ModeError("Cannot start training mode") from exc

    def submit_guess(self, guess: str) -> List[str]:
        """
        Submit a guess for the current training game.

        Args:
            guess: Word guessed by the player.

        Returns:
            Result of the guess evaluation.

        Raises:
            ModeError: If no game is active.
        """
        if self.current_game is None:
            logger.error("Attempted guess without active training game.")
            raise ModeError("No active game")

        result = self.current_game.check_guess(guess)
        return result
