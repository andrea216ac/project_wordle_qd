import random

class WordProvider:
    """
    Fornisce parole casuali per il gioco.
    Può essere collegato a un database o a file in futuro.
    """

    def __init__(self, words):
        """
        words: lista di parole disponibili
        """
        self.words = words

    def get_random_word(self):
        """
        Restituisce una parola casuale dalla lista.
        """
        return random.choice(self.words)