"""Modulo di test per il repository degli utenti."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User
from src.database.user_repository import UserRepository


@pytest.fixture
def db_session():
    """Prepara un database SQLite in memoria vuoto e isolato per i test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()


class TestUserRepository:
    """Suite di test per verificare le operazioni CRUD sugli utenti."""

    # pylint: disable=redefined-outer-name

    def test_create_user(self, db_session):
        """Testa che la creazione di un utente avvenga con i valori corretti."""
        repo = UserRepository(db_session)
        nuovo_utente = repo.create_user("Andrea")

        assert nuovo_utente is not None
        assert nuovo_utente.username == "Andrea"

    def test_get_user_by_username_existing(self, db_session):
        """Testa il recupero di un utente precedentemente salvato."""
        repo = UserRepository(db_session)
        repo.create_user("Marco")

        utente_trovato = repo.get_user_by_username("Marco")

        assert utente_trovato is not None
        assert utente_trovato.username == "Marco"

    def test_get_user_by_username_not_found(self, db_session):
        """Testa il comportamento del repository con un utente inesistente."""
        repo = UserRepository(db_session)

        utente_fantasma = repo.get_user_by_username("UtenteFantasma")

        assert utente_fantasma is None

    def test_create_user_already_exists(self, db_session):
        """Testa la riga 35: creazione di un utente già presente nel database."""
        repo = UserRepository(db_session)
        repo.create_user("Giulia")

        # Ritenta la creazione dello stesso identico utente
        utente_esistente = repo.create_user("Giulia")

        assert utente_esistente is not None
        assert utente_esistente.username == "Giulia"

    def test_get_user_by_username_db_error(self):
        """Testa le righe 26-28: gestione delle eccezioni durante la query."""
        mock_session = MagicMock()
        # Istruiamo la finta sessione a lanciare un errore fatale quando viene interrogata
        mock_session.query.side_effect = SQLAlchemyError("Errore simulato di lettura")

        repo = UserRepository(mock_session)
        risultato = repo.get_user_by_username("TestError")

        assert risultato is None

    def test_create_user_db_error(self):
        """Testa le righe 43-50: gestione delle eccezioni in scrittura e rollback."""
        mock_session = MagicMock()

        # Facciamo finta che l'utente non esista per poter procedere alla creazione
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query

        # Il salvataggio esplode simulando un errore del server
        mock_session.commit.side_effect = SQLAlchemyError(
            "Errore simulato di scrittura"
        )

        repo = UserRepository(mock_session)
        risultato = repo.create_user("UtenteSfortunato")

        assert risultato is None
        # Verifica vitale: il sistema deve aver annullato la transazione guasta (rollback)
        mock_session.rollback.assert_called_once()
