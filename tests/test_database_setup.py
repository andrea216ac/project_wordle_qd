"""Modulo di test avanzato per l'inizializzazione e il popolamento del database."""

import logging
from unittest.mock import MagicMock, mock_open, patch

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

from src.database.init_db import init_database
from src.database.models import Base, Word
from src.database.seed_db import seed_words_from_file


def test_init_database():
    """Verifica che init_database crei le tabelle correttamente."""
    engine = create_engine("sqlite:///:memory:")
    with patch("src.database.init_db.engine", engine):
        init_database()

    inspector = inspect(engine)
    assert "users" in inspector.get_table_names()


def test_seed_words_from_file_success():
    """Testa il caricamento con successo e il filtraggio parole brevi."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    file_content = "GATTO\nRE\nCANE\n"  # Solo GATTO è da 5

    with patch("src.database.seed_db.engine", engine):
        with patch("src.database.seed_db.SessionLocal") as mock_session_cls:
            from sqlalchemy.orm import sessionmaker

            session = sessionmaker(bind=engine)()
            mock_session_cls.return_value.__enter__.return_value = session

            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.open", mock_open(read_data=file_content)):
                    seed_words_from_file("fake.txt", "IT", length=5)

            assert session.query(Word).count() == 1
            session.close()


def test_seed_words_db_error():
    """Testa la riga dell'eccezione SQLAlchemyError in seed_db (copertura 100%)."""
    with patch("src.database.seed_db.SessionLocal") as mock_session_cls:
        session = MagicMock()
        # Simula un errore al momento del commit
        session.commit.side_effect = SQLAlchemyError("Errore DB")
        mock_session_cls.return_value.__enter__.return_value = session

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.open", mock_open(read_data="PAROLA\n")):
                # Non deve crashare, ma gestire l'errore
                seed_words_from_file("error.txt", "IT", length=6)

        session.rollback.assert_called()


def test_seed_words_empty_file():
    """Testa il caso di file vuoto per coprire il warning log."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.open", mock_open(read_data="")):
            seed_words_from_file("empty.txt", "IT")
