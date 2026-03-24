# pylint: disable=duplicate-code
"""Modulo di test per il repository del dizionario di parole."""

import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Word
from src.database.word_repository import WordRepository


@pytest.fixture
def db_session():
    """Prepara un database SQLite in memoria vuoto e isolato per i test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()


class TestWordRepository:
    """Suite di test per verificare l'estrazione delle parole."""

    # pylint: disable=redefined-outer-name

    def test_get_random_word_success(self, db_session):
        """Testa il corretto recupero di una parola casuale."""
        repo = WordRepository(db_session)
        word = Word(word="GATTO", language="IT", length=5)
        db_session.add(word)
        db_session.commit()

        risultato = repo.get_random_word(language="IT", length=5)

        assert risultato is not None
        assert risultato.word == "GATTO"

    def test_get_random_word_db_error(self):
        """Testa la gestione delle eccezioni in get_random_word."""
        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError("Errore DB")

        repo = WordRepository(mock_session)
        risultato = repo.get_random_word()

        assert risultato is None

    def test_get_daily_word_success(self, db_session):
        """Testa il recupero di una parola giornaliera con seed deterministico."""
        repo = WordRepository(db_session)
        parole = [
            Word(word="ALBER", language="IT", length=5),
            Word(word="GATTO", language="IT", length=5),
            Word(word="FIORE", language="IT", length=5),
        ]
        db_session.add_all(parole)
        db_session.commit()

        data_test = datetime.date(2026, 3, 24)

        # Estraiamo la parola due volte con la stessa data per verificare il seed
        risultato_1 = repo.get_daily_word(data_test, language="IT", length=5)
        risultato_2 = repo.get_daily_word(data_test, language="IT", length=5)

        assert risultato_1 is not None
        assert risultato_1.word == risultato_2.word

    def test_get_daily_word_no_words(self, db_session):
        """Testa get_daily_word quando il database è vuoto."""
        repo = WordRepository(db_session)
        data_test = datetime.date(2026, 3, 24)

        risultato = repo.get_daily_word(data_test)

        assert risultato is None

    def test_get_daily_word_db_error(self):
        """Testa la gestione delle eccezioni in get_daily_word."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.side_effect = SQLAlchemyError("Errore DB")
        mock_session.query.return_value = mock_query

        repo = WordRepository(mock_session)
        data_test = datetime.date(2026, 3, 24)
        risultato = repo.get_daily_word(data_test)

        assert risultato is None

    def test_word_exists_true(self, db_session):
        """Testa word_exists quando la parola è presente (case-insensitive)."""
        repo = WordRepository(db_session)
        word = Word(word="GATTO", language="IT", length=5)
        db_session.add(word)
        db_session.commit()

        assert repo.word_exists("gatto", "it") is True
        assert repo.word_exists("GATTO", "IT") is True

    def test_word_exists_false(self, db_session):
        """Testa word_exists quando la parola non è presente."""
        repo = WordRepository(db_session)
        word = Word(word="GATTO", language="IT", length=5)
        db_session.add(word)
        db_session.commit()

        assert repo.word_exists("cane", "it") is False
        assert repo.word_exists("GATTO", "EN") is False

    def test_word_exists_db_error(self):
        """Testa la gestione delle eccezioni in word_exists."""
        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError("Errore DB")

        repo = WordRepository(mock_session)
        risultato = repo.word_exists("test", "it")

        assert risultato is False
