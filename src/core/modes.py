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

    
