"""Configurazione globale per le fixture di Pytest."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base


@pytest.fixture
def db_session():
    """Prepara un database in memoria isolato per i test reali."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()
