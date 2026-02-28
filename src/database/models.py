from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base  # Importiamo la 'Base' magica che hai creato poco fa!

# Tabella degli UTENTI
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    
    # Relazione: un utente può avere tante partite. 
    # Questo ci permetterà di chiedere a Python: "utente.games" e riavere tutte le sue giocate!
    games = relationship("Game", back_populates="player")


# Tabella delle PARTITE
class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    
    # Chiave Esterna (Foreign Key): collega questa partita all'ID di un utente specifico
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    word_to_guess = Column(String, nullable=False)       # La parola segreta
    attempts = Column(Integer, nullable=False)           # Quanti tentativi ha usato (1-6)
    won = Column(Boolean, nullable=False, default=False) # Ha vinto o perso?
    points = Column(Integer, nullable=False, default=0)  # Punti calcolati (es. 6 punti al 1° colpo)
    mode = Column(String, nullable=False)                # "Daily" o "Training"
    played_at = Column(DateTime, default=datetime.now)   # Data e ora esatta
    
    # Relazione inversa: collega la partita al suo giocatore
    player = relationship("User", back_populates="games")