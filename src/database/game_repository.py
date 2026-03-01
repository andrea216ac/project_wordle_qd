from sqlalchemy.orm import Session
from src.database.models import Game

class GameRepository:
    """
    Gestisce tutte le operazioni nel database per la tabella 'games'.
    Isola la logica di salvataggio e recupero delle partite.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def save_game(self, user_id: int, word_to_guess: str, attempts: int, won: bool, points: int, mode: str) -> Game:
        """
        Salva il risultato di una partita appena conclusa.
        Collega automaticamente la partita al giocatore tramite il suo user_id.
        """
        new_game = Game(
            user_id=user_id,
            word_to_guess=word_to_guess,
            attempts=attempts,
            won=won,
            points=points,
            mode=mode
        )
        
        self.session.add(new_game)
        self.session.commit()
        self.session.refresh(new_game)
        
        return new_game

    def get_games_by_user(self, user_id: int) -> list[Game]:
        """
        Recupera tutto lo storico delle partite di un giocatore specifico.
        Perfetto per creare una schermata "Statistiche" nell'interfaccia grafica!
        """
        return self.session.query(Game).filter(Game.user_id == user_id).all()