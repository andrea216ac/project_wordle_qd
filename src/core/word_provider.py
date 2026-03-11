"""Word Provider fornisce parole casuali."""

import datetime
import logging
import random
from typing import Dict, List, Set


logger = logging.getLogger(__name__)


class WordProvider:  # pylint: disable=too-few-public-methods
    """Fornisce parole per il gioco supportando diverse lingue.."""

    def __init__(self, words_by_language: Dict[str, List[str]]) -> None:
        """
        Inizializzazione

        Args:
            words_by_language: Dictionary mapping language codes to word lists.
        """
        self.words_by_language: Dict[str, List[str]] = words_by_language
        self.used_words: Dict[str, Set[str]] = {
            language: set() for language in words_by_language
        }


    def get_random_word(self, language: str, length: int) -> str:
        """
        Restituisce una parola casuale per una determinata lingua e lunghezza.

        Le parole già utilizzate in modalità allenamento non verranno ripetute.

        Args:
            language: Language code (e.g. "it", "en").
            length: Desired word length.

        Returns:
            A random word.

        Raises:
            ValueError: If no valid words are available.
        """
        words = self.words_by_language.get(language)

        if words is None:
            logger.error("Language '%s' not available.", language)
            raise ValueError("Language not available")

        filtered_words = [word for word in words if len(word) == length]

        if not filtered_words:
            logger.error(
                "No words available for language '%s' with length %s.",
                language,
                length,
            )
            raise ValueError("No words available for the requested length")

        available_words = [
            word for word in filtered_words if word not in self.used_words[language]
        ]

        if not available_words:
            logger.info(
                "All words used for language '%s'. Resetting used words.",
                language,
            )
            self.used_words[language].clear()
            available_words = filtered_words

        chosen_word = random.choice(available_words)

        self.used_words[language].add(chosen_word)

        return chosen_word


    def get_daily_word(self, language: str, length: int) -> str:
        """
        Restituisci la parola del giorno per una determinata lingua.

        Verrà restituita la stessa parola per l'intera giornata.

        Args:
            language: Language code.
            length: Desired word length.

        Returns:
            Word of the day.

        Raises:
            ValueError: If the language or words are not available.
        """
        words = self.words_by_language.get(language)

        if words is None:
            logger.error("Language '%s' not available.", language)
            raise ValueError("Language not available")

        filtered_words = [word for word in words if len(word) == length]

        if not filtered_words:
            logger.error(
                "No daily words available for language '%s' with length %s.",
                language,
                length,
            )
            raise ValueError("No words available for the requested length")

        today_index = datetime.date.today().toordinal() % len(filtered_words)

        return filtered_words[today_index]
