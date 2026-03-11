"""Core game logic module for Wordle."""

import logging
from typing import Optional, List


logger = logging.getLogger(__name__)


class Game:
    """Represents a single Wordle game session."""

    def __init__(self, target_word: str, max_attempts: int = 6) -> None:
        """
        Initialize the game.

        Args:
            target_word: The word to guess.
            max_attempts: Maximum number of attempts allowed.
        """
        self.target_word: str = target_word
        self.attempts: int = 0
        self.is_over: bool = False
        self.max_attempts: int = max_attempts
     
    # ==== METODO INDOVINA =====
    def check_guess(self, guess):

        #CONTROLLO SE GIOCO E' FINITO
        if self.is_over:
            raise Exception("Il gioco è finito")   #interfaccia
        
        #CONTROLLO LUNGHEZZA
        if len(guess) != len(self.target_word):
            raise ValueError("Lunghezza non valida") #interfaccia
        
        #CONTROLLO CARATTERI 
        if not guess.isalpha():
            raise ValueError("La parola deve contenere solo lettere")
        
        self.attempts += 1                         #incremento tentativo
        result = [None] * len(self.target_word)    #result: array per corretto, presente o assente
        usato = [False] * len(self.target_word)    #usato: stringa booleana, evita riutilizzo delle lettere

        #CICLO PER PAROLE CORRETTE
        for i in range(len(self.target_word)):
            if guess[i] == self.target_word[i]: 
                result[i] = "Corretto" 
                usato[i] = True 

        #CICLO PER PRESENTE E ASSENTE 
        for i in range(len(self.target_word)): #scorre la parola "guess" e array "result"
            if result[i] is None:   # solo lettere non corrette 
                trovato = False

                for j in range(len(self.target_word)):  #scorre la parola "target" e array "usato"
                    #se lettera presente ma non "usata"
                    if guess[i] == self.target_word[j] and not usato[j]: 
                        trovato = True
                        usato[j] = True
                        break              

                if trovato:    
                    result[i] = "Presente"     #esempio palla - lampa (presente, corretto, assente, presente, corretto)
                else: 
                    result[i] = "Assente"      #lettere doppie ma già usate es. cassa - sassi 

        #CONTROLLO VITTORIA E FINE TENTATIVI
        if all(r == "Corretto" for r in result):   #interfaccia
            self.is_over = True
        elif self.attempts >= self.max_attempts:  # print tentativi finiti (UI)
            self.is_over = True

        return result
