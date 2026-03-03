"""Modulo per l'inizializzazione del database e la creazione delle tabelle."""

import src.database.models  # pylint: disable=unused-import
from src.database.db import Base, engine


def init_database() -> None:
    """Crea il database e tutte le tabelle definite nei modelli."""
    print("Creazione del database in corso...")
    Base.metadata.create_all(bind=engine)
    print("Database 'wordle.db' e tabelle creati con successo! 🎉")


if __name__ == "__main__":
    init_database()
