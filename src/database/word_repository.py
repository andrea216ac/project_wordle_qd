"""Modulo contenente il repository per la gestione del dizionario di parole."""

import datetime
import logging
import random

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from src.database.models import Word

logger = logging.getLogger(__name__)


class WordRepository:
    """Gestisce l'estrazione e la manipolazione delle parole nel database."""

    def __init__(self, session: Session) -> None:
        """Inizializza il repository con la sessione del database."""
        self.session = session

    def get_random_word(self, language: str = "IT", length: int = 5) -> Word | None:
        """Recupera una parola casuale per la modalità allenamento (infinita)."""
        try:
            return (
                self.session.query(Word)
                .filter(Word.language == language, Word.length == length)
                .order_by(func.random())  # pylint: disable=not-callable
                .first()
            )
        except SQLAlchemyError as error:
            logger.error(
                "Errore DB durante recupero parola casuale (%s): %s",
                language,
                error,
            )
            return None

    def get_daily_word(
        self, target_date: datetime.date, language: str = "IT", length: int = 5
    ) -> Word | None:
        """
        Recupera la parola del giorno, identica per tutti i giocatori.
        Utilizza la data come seed matematico per garantire lo stesso risultato.
        """
        try:
            query = self.session.query(Word).filter(
                Word.language == language, Word.length == length
            )
            total_words = query.count()

            if total_words == 0:
                return None

            # Creiamo un seed univoco combinando data, lingua e lunghezza
            seed_string = f"{target_date.isoformat()}-{language}-{length}"
            rng = random.Random(seed_string)

            # Estraiamo un indice "casuale" ma sempre identico per lo stesso seed
            chosen_index = rng.randint(0, total_words - 1)

            # offset() salta le righe fino all'indice scelto e prende la prima
            return query.offset(chosen_index).first()

        except SQLAlchemyError as error:
            logger.error(
                "Errore DB durante recupero parola giornaliera (%s): %s",
                language,
                error,
            )
            return None
