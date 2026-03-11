"""WordProvider fornisce parole casuali"""

import random
import logging
from typing import List


logger = logging.getLogger(__name__)


class WordProvider:
    """
    Fornisce parole casuali per il gioco.
    Da sostituire con database
    """

    def __init__(self, words: List[str]) -> None:
        """
        Initialize the provider with a list of words.

        Args:
            words (List[str]): List of available words.
        """
        self.words = words

    def get_random_word(self) -> str:
        """
        Return a random word from the list.

        Returns:
            str: A randomly selected word.
        """
        try:
            word = random.choice(self.words)
            return word

        except IndexError as exc:
            logger.error("WordProvider has no words available.", exc_info=exc)
            raise ValueError("No words available in provider.") from exc