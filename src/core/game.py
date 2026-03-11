"""Game logic per Wordle."""

import logging
from typing import Optional, List


logger = logging.getLogger(__name__)


class Game:
    """Rappresenta una singola sessione del gioco Wordle"""

    def __init__(self, target_word: str, max_attempts: int = 6) -> None:
        """
        Inizializzazione the game.

        Args:
            target_word: Parola da indovinare.
            max_attempts: Numero massimo di tentativi possibili.
        """
        self.target_word: str = target_word
        self.attempts: int = 0
        self.is_over: bool = False
        self.max_attempts: int = max_attempts
     
    def check_guess(self, guess: str) -> List[str]:
        """
        Confrontare la risposta del giocatore con la parola da indovinare.

        Args:
            guess: Parola indovinata dal giocatore.

        Returns:
            List of strings: "Corretto", "Presente" or "Assente".

        Raises:
            ValueError: Se le lunghezze non corrispondono.
            RuntimeError: Se il gioco è già finito.
        """
        if self.is_over:
            logger.error("Attempted guess after game is over.")
            raise RuntimeError("Game is already over")

        if len(guess) != len(self.target_word):
            logger.error(
                "Invalid guess length: expected %d, got %d",
                len(self.target_word),
                len(guess),
            )
            raise ValueError("Invalid guess length")

        self.attempts += 1
        result: List[Optional[str]] = [None] * len(self.target_word)
        used: List[bool] = [False] * len(self.target_word)

        # 1° pass: corretto
        for i, char in enumerate(guess):
            if char == self.target_word[i]:
                result[i] = "Corretto"
                used[i] = True

        # 2° pass: presente
        for i, char in enumerate(guess):
            if result[i] is None:
                found = False
                for j, target_char in enumerate(self.target_word):
                    if char == target_char and not used[j]:
                        found = True
                        used[j] = True
                        break
                result[i] = "Presente" if found else "Assente"

        #CONTROLLO VITTORIA E FINE TENTATIVI
        if all(r == "Corretto" for r in result):   #interfaccia
            self.is_over = True
        elif self.attempts >= self.max_attempts:  # print tentativi finiti (UI)
            self.is_over = True

        return result
