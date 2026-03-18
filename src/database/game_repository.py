"""Modulo contenente il repository per l'accesso ai dati delle partite."""

import datetime
import logging

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models import Game, User

logger = logging.getLogger(__name__)


class GameRepository:
    """Gestisce le operazioni CRUD nel database per l'entità Game."""

    def __init__(self, session: Session) -> None:
        """Inizializza il repository con la sessione."""
        self.session = session

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def save_game(
        self,
        user_id: int,
        word_to_guess: str,
        attempts: int,
        won: bool,
        points: int,
        mode: str,
    ) -> Game | None:
        """Salva i risultati di una nuova partita nel database."""
        try:
            new_game = Game(
                user_id=user_id,
                word_to_guess=word_to_guess,
                attempts=attempts,
                won=won,
                points=points,
                mode=mode,
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
                error,
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
                error,
            )
            return []

    def has_played_today(self, user: str) -> bool:
        """
        Verifica se l'utente specificato (tramite username) ha già
        completato una partita classica nella giornata odierna.
        """
        try:
            db_user = self.session.query(User).filter(User.username == user).first()
            if not db_user:
                return False

            today = datetime.date.today()

            # Assumiamo che la colonna della data si chiami 'date' nel tuo models.py.
            game_today = (
                self.session.query(Game)
                .filter(
                    Game.user_id == db_user.id,
                    Game.mode == "classic",
                    func.date(Game.played_at) == today,
                )
                .first()
            )

            return game_today is not None

        except SQLAlchemyError as error:
            logger.error(
                "Errore DB in has_played_today per l'utente %s: %s",
                user,
                error,
            )
            return False

    def save_score(self, user: str, score: int, attempts: int) -> None:
        """
        Adattatore per GameManager. Riceve username, punteggio e tentativi,
        compila i campi mancanti e chiama il metodo principale save_game.
        """
        try:
            db_user = self.session.query(User).filter(User.username == user).first()
            if not db_user:
                logger.error("Utente %s non trovato. Salvataggio annullato.", user)
                return

            won = attempts <= 6 and score > 0
            word_to_guess = "SCONOSCIUTA"
            mode = "classic"

            self.save_game(
                user_id=db_user.id,  # type: ignore[arg-type]
                word_to_guess=word_to_guess,
                attempts=attempts,
                won=won,
                points=score,
                mode=mode,
            )

            logger.info("Score salvato con successo tramite adattatore per %s", user)

        except Exception as error:  # pylint: disable=broad-exception-caught
            logger.error("Errore critico nell'adattatore save_score: %s", error)

    def get_leaderboard_data(self, limit: int = 10) -> list[tuple[str, int]]:
        """Recupera la classifica generale sommando i punti di ogni utente."""
        try:
            # Esegue: SELECT username, SUM(points) FROM users JOIN games ...
            results = (
                self.session.query(
                    User.username, func.sum(Game.points).label("total_score")
                )
                .join(Game, User.id == Game.user_id)
                .group_by(User.id, User.username)
                .order_by(func.sum(Game.points).desc())
                .limit(limit)
                .all()
            )
            # Converte il risultato di SQLAlchemy in una semplice lista di tuple
            return [(row.username, int(row.total_score or 0)) for row in results]
        except SQLAlchemyError as error:
            logger.error("Errore DB in get_leaderboard_data: %s", error)
            return []

    def save_game_state(self, user: str, state_data: str) -> None:
        """Salva lo stato della partita in sospeso (es. JSON) per l'utente."""
        try:
            db_user = self.session.query(User).filter(User.username == user).first()
            if db_user:
                db_user.saved_state = state_data # type: ignore[assignment]
                self.session.commit()
                logger.info("Stato partita salvato con successo per %s", user)
            else:
                logger.warning("Utente %s non trovato. Salvataggio ignorato.", user)
        except SQLAlchemyError as error:
            self.session.rollback()
            logger.error("Errore critico DB in save_game_state: %s", error)

    def load_game_state(self, user: str) -> str | None:
        """Carica lo stato della partita in sospeso dell'utente, se esiste."""
        try:
            db_user = self.session.query(User).filter(User.username == user).first()
            return db_user.saved_state if db_user else None # type: ignore[return-value]
        except SQLAlchemyError as error:
            logger.error("Errore DB in load_game_state: %s", error)
            return None
