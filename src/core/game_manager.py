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