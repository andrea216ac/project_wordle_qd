"""Modulo contenente il repository per l'accesso ai dati degli utenti."""

from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Gestisce le operazioni CRUD nel database per l'entità User."""

    def __init__(self, session: Session) -> None:
        """Inizializza il repository con la sessione."""
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        """Cerca un utente in base allo username."""
        try:
            return self.session.query(User).filter(User.username == username).first()
        except SQLAlchemyError as error:
            logger.error("Errore DB in get_user_by_username: %s", error)
            return None

    def create_user(self, username: str) -> User | None:
        """Crea un nuovo utente o restituisce quello esistente."""
        try:
            existing_user = self.get_user_by_username(username)
            if existing_user:
                return existing_user

            new_user = User(username=username)
            self.session.add(new_user)
            self.session.commit()
            self.session.refresh(new_user)
            return new_user

        except SQLAlchemyError as error:
            self.session.rollback()
            logger.error(
                "Errore critico durante la creazione dell'utente '%s': %s",
                username,
                error,
            )
            return None
