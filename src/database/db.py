"""Modulo per la configurazione del database e la gestione delle sessioni."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.getenv("WORDLE_DB_URL", "sqlite:///wordle.db")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False}, echo=False)

# pylint: disable=invalid-name
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
