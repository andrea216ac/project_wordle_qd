"""Modulo contenente il repository per l'accesso ai dati delle partite."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import Game

logger = logging.getLogger(__name__)


class GameRepository:
    """Gestisce le operazioni CRUD nel database per l'entità Game."""

    def __init__(self, session: Session) -> None:
        """Inizializza il repository con la sessione."""
        self.session = session

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def save_game(
        self, user_id: int, word_to_guess: str, attempts: int, won: bool, points: int, mode: str
    ) -> Game | None:
        """Salva i risultati di una nuova partita nel database."""
        try:
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

        except SQLAlchemyError as error:
            self.session.rollback()
            logger.error(
                "Errore critico durante salvataggio partita per user_id %s: %s",
                user_id,
                error
            )
            return None

    def get_games_by_user(self, user_id: int) -> list[Game]:
        """Recupera lo storico di tutte le partite giocate da uno specifico utente."""
        try:
            return self.session.query(Game).filter(Game.user_id == user_id).all()
        except SQLAlchemyError as error:
            logger.error(
                "Errore DB durante il recupero dello storico per user_id %s: %s",
                user_id,
                error
            )
            return []
