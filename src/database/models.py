"""Modulo contenente le definizioni dei modelli ORM per il database."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.db import Base


class User(Base):
    """
    Rappresenta un giocatore registrato nell'applicazione.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    # Relazione bidirezionale con le partite (Uno-a-Molti)
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

    # Relazione inversa verso l'utente
    user = relationship("User", back_populates="games")
