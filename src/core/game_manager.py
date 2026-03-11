"""Game manager coordina le sessioni di gioco."""

import logging
from typing import Optional, List

from src.core.game import Game
from src.core.word_provider import WordProvider
from src.core.modes import ClassicMode, TrainingMode, ModeError


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

    # Avvia modalità classica (parola del giorno + punteggio)
    def start_classic(self):
        self.mode = ClassicMode(self.word_provider)
        self.mode.start()

    # Avvia modalità allenamento (parole random, infinite, senza punteggio)
    def start_training(self):
        self.mode = TrainingMode(self.word_provider)
        self.mode.start()

    # Invia un guess alla modalità corrente
    def make_guess(self, guess: str):
        if self.mode is None:
            raise Exception("Nessuna partita attiva")
        return self.mode.make_guess(guess)

    # Controlla se la partita è finita
    def is_game_over(self) -> bool:
        if self.mode is None:
            return False
        return self.mode.game.is_over

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