"""Modulo per la configurazione del database e la gestione delle sessioni."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Recupera il percorso del DB dalle variabili di ambiente, con fallback al file locale
DB_PATH = os.getenv("WORDLE_DB_URL", "sqlite:///wordle.db")

# Creazione dell'engine. echo=False evita di spammare log SQL nel terminale
engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False},  # Necessario per SQLite
    echo=False
)

# Configurazione della fabbrica di sessioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base dichiarativa per i modelli
Base = declarative_base()