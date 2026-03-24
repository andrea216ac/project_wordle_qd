"""Modulo di test completo e definitivo per GameRepository."""

import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.database.game_repository import GameRepository
from src.database.models import Base, Game, User


@pytest.fixture
def db_session():
    """Prepara un database in memoria isolato per i test reali."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


class TestGameRepositoryFinal:
    """Suite finale per coprire ogni riga di game_repository.py."""

    # pylint: disable=redefined-outer-name

    def test_save_game_success(self, db_session):
        """Testa il salvataggio normale e il recupero dati."""
        repo = GameRepository(db_session)
        user = User(username="Angelo")
        db_session.add(user)
        db_session.commit()

        res = repo.save_game(user.id, "GATTO", 3, True, 100, "classic")
        assert res is not None
        assert res.word_to_guess == "GATTO"
        
        # Verifica anche get_games_by_user (Righe 58-60)
        history = repo.get_games_by_user(user.id)
        assert len(history) == 1

    def test_save_game_exception(self):
        """Forza SQLAlchemyError durante il salvataggio per coprire il rollback (Righe 42-50)."""
        mock_session = MagicMock()
        mock_session.commit.side_effect = SQLAlchemyError("DB Crash")
        repo = GameRepository(mock_session)
        
        res = repo.save_game(1, "TEST", 1, True, 10, "classic")
        assert res is None
        mock_session.rollback.assert_called_once()

    def test_get_games_error(self):
        """Forza errore nel recupero storico (Righe 61-65)."""
        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError("Error")
        repo = GameRepository(mock_session)
        assert repo.get_games_by_user(1) == []

    def test_has_played_today_flow(self, db_session):
        """Testa il flusso di gioco giornaliero e utente non trovato (Righe 71-105)."""
        repo = GameRepository(db_session)
        
        # Caso utente non esiste
        assert repo.has_played_today("Inesistente") is False
        
        # Caso utente esiste ma non ha giocato
        u = User(username="Player1")
        db_session.add(u)
        db_session.commit()
        assert repo.has_played_today("Player1") is False
        
        # Caso ha giocato oggi
        repo.save_game(u.id, "GATTO", 1, True, 10, "classic")
        assert repo.has_played_today("Player1") is True

    def test_has_played_today_exception(self):
        """Forza errore DB in has_played_today (Righe 100-104)."""
        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError("Error")
        repo = GameRepository(mock_session)
        assert repo.has_played_today("Angelo") is False

    def test_save_score_adapter_and_error(self, db_session):
        """Testa l'adattatore save_score e il caso utente mancante (Righe 112-140)."""
        repo = GameRepository(db_session)
        
        # Utente non trovato nell'adattatore
        repo.save_score("Ghost", 100, 3) 
        
        # Successo adattatore
        u = User(username="AdapterUser")
        db_session.add(u)
        db_session.commit()
        repo.save_score("AdapterUser", 50, 4)
        
        game = db_session.query(Game).filter(Game.user_id == u.id).first()
        assert game.points == 50

    def test_leaderboard_data_complete(self, db_session):
        """Testa classifica reale ed errore DB (Righe 146-180)."""
        repo = GameRepository(db_session)
        u = User(username="Winner")
        db_session.add(u)
        db_session.commit()
        repo.save_game(u.id, "W", 3, True, 10, "classic")
        
        lb = repo.get_leaderboard_data()
        assert lb[0]["utente"] == "Winner"
        
        # Forza errore DB
        with patch.object(db_session, "query", side_effect=SQLAlchemyError("Error")):
            assert repo.get_leaderboard_data() == []

    def test_game_state_flow_and_error(self, db_session):
        """Testa salvataggio/caricamento stato e relativi errori (Righe 186-213)."""
        repo = GameRepository(db_session)
        u = User(username="StateUser")
        db_session.add(u)
        db_session.commit()
        
        # Successo
        repo.save_game_state("StateUser", '{"r": 1}')
        assert repo.load_game_state("StateUser") == '{"r": 1}'
        
        # Utente non trovato
        repo.save_game_state("NoUser", "{}")
        assert repo.load_game_state("NoUser") is None
        
        # Errore DB in caricamento
        with patch.object(db_session, "query", side_effect=SQLAlchemyError("Error")):
            assert repo.load_game_state("StateUser") is None

# Import necessario per il patch
from unittest.mock import patch