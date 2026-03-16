"""Word Provider usa WordRepository per ottenere parole dal database."""

import datetime
import logging

from src.database.word_repository import WordRepository

logger = logging.getLogger(__name__)


class WordProvider:  # pylint: disable=too-few-public-methods
    """Fornisce parole al gioco usando WordRepository."""

    def __init__(self, word_repository: WordRepository) -> None:
        self.word_repository = word_repository
        self.word_length = 5

    def get_random_word(self, language: str) -> str:
        """Restituisce una parola casuale per la modalità training."""
        word = self.word_repository.get_random_word(language, self.word_length)

        if word is None:
            logger.error("No random word available")
            raise ValueError("Language not available")

        return word.text

    def get_daily_word(self, language: str, length: int) -> str:
        """Restituisce la parola del giorno."""
        today = datetime.date.today()

        word = self.word_repository.get_daily_word(
            today,
            language,
            self.word_length,
        )

        if word is None:
            logger.error("No daily word available")
            raise ValueError("No word available")

        return word.text