"""Modulo contenente le definizioni dei modelli ORM per il database."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.db import Base


class User(Base):
    """Rappresenta un giocatore registrato nell'applicazione."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    games = relationship("Game", back_populates="user", cascade="all, delete-orphan")


class Game(Base):
    """
    Rappresenta una singola partita giocata da un utente.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    word_to_guess = Column(String, nullable=False)
    attempts = Column(Integer, nullable=False)
    won = Column(Boolean, nullable=False)
    points = Column(Integer, nullable=False)
    mode = Column(String, nullable=False)

    # NUOVA COLONNA: Salva automaticamente data e ora correnti
    played_at = Column(
        DateTime, default=func.now(), nullable=False  # pylint: disable=not-callable
    )
    user = relationship("User", back_populates="games")


class Word(Base):
    """
    Rappresenta una parola del dizionario multilingua.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    language = Column(String, nullable=False, index=True)
    length = Column(Integer, nullable=False)
