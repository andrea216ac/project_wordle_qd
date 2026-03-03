"""
Modulo contenente la logica principale del gioco Wordle.
"""


class WordleGame:
    """
    Classe che gestisce lo stato e le regole di una partita Wordle.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, secret_word="GATTO"):
        """Inizializza il gioco con una parola segreta."""
        self.secret_word = secret_word.upper()

    def get_welcome_message(self):
        """Restituisce il messaggio di benvenuto per il debug."""
        return "Connessione"
