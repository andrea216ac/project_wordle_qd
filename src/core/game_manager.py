from modes import ClassicMode, TrainingMode
from word_provider import WordProvider

class GameManager:
    """
    Coordina il gioco, scegliendo la modalità e collegando
    le chiamate della UI alla logica del gioco.
    """

    def __init__(self, word_provider: WordProvider):
        self.word_provider = word_provider
        self.mode = None  # ClassicMode o TrainingMode

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

    # Ritorna il punteggio (solo modalità classica)
    def get_score(self):
        if hasattr(self.mode, "score"):
            return self.mode.score
        return None

    # Avvia una nuova partita nella modalità corrente
    def next_game(self):
        if self.mode is None:
            raise Exception("Nessuna modalità attiva")
        self.mode.start()