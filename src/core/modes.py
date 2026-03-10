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