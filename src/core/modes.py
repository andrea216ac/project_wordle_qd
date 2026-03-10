"""Modalità di Gioco: ClassicMode and TrainingMode."""

import datetime
import logging
import random
from typing import Optional

from word_provider import WordProvider
from game import Game


logger = logging.getLogger(__name__)

# Metodo Classico: una parola al giorno
class ClassicMode:
    
    #costruttore
    def __init__(self, word_provider: WordProvider) -> None:
        
        self.word_provider = word_provider
        self.game: Optional[Game] = None
        self.score: int = 0
        self.current_word: Optional[str] = None

    #Inizio partita con la parola del giorno
    def start(self) -> None:
        
        try:
            words = self.word_provider.words
            today = datetime.date.today()
            index = today.toordinal() % len(words)
            self.current_word = words[index]
            self.game = Game(self.current_word)

        except Exception as exc:
            logger.error("Impossibile avviare ClassicMode.", exc_info=exc)
            raise

    def make_guess(self, guess: str) -> list[str]:
        
        if self.game is None:
            raise Exception("ClassicMode game not started.")

        result = self.game.check_guess(guess)

        if guess == self.current_word:
            self.score += self.game.max_attempts - self.game.attempts + 1

        return result


class TrainingMode:
    def __init__(self, word_provider: WordProvider) -> None:
       
        self.word_provider = word_provider
        self.used_words: set[str] = set()
        self.game: Optional[Game] = None

    def start(self) -> None:
        
        try:
            available_words = [
                w for w in self.word_provider.words if w not in self.used_words
            ]

            if not available_words:
                self.used_words.clear()
                available_words = self.word_provider.words.copy()

            word = random.choice(available_words)
            self.used_words.add(word)
            self.game = Game(word)

        except Exception as exc:
            logger.error("Failed to start TrainingMode.", exc_info=exc)
            raise

    def make_guess(self, guess: str) -> list[str]:
     
        if self.game is None:
            raise Exception("TrainingMode game not started.")

        return self.game.check_guess(guess)