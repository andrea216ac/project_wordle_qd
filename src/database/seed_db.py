"""Script per il popolamento massivo del database con le parole di gioco."""

import logging
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from src.database.db import SessionLocal
from src.database.models import Word

logger = logging.getLogger(__name__)


def seed_words_from_file(file_path: str, language: str, length: int = 5) -> None:
    """
    Legge un file di testo e inserisce le parole valide nel database.
    Evita i duplicati controllando le parole già presenti.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error("File non trovato: %s", file_path)
        return

    with path.open("r", encoding="utf-8") as file:
        # Estrae le parole: rimuove spazi, mette in maiuscolo, filtra per lunghezza
        raw_words = {
            line.strip().upper() for line in file if len(line.strip()) == length
        }

    if not raw_words:
        logger.warning("Nessuna parola valida trovata in %s", file_path)
        return

    with SessionLocal() as session:
        try:
            # Recupera le parole già presenti per evitare duplicati
            existing = (
                session.query(Word.word)
                .filter(
                    Word.language == language,
                    Word.length == length,
                )
                .all()
            )

            existing_words = {w.word for w in existing}
            new_words = raw_words - existing_words

            if not new_words:
                logger.info("Tutte le parole di %s sono già presenti.", file_path)
                return

            # Prepara gli oggetti Word per l'inserimento
            words_to_insert = [
                Word(word=w, language=language, length=length) for w in new_words
            ]

            # Inserimento massivo (bulk insert)
            session.add_all(words_to_insert)
            session.commit()

            logger.info(
                "Inserite %d nuove parole (%s) dal file %s.",
                len(words_to_insert),
                language,
                file_path,
            )

        except SQLAlchemyError as error:
            session.rollback()
            logger.error(
                "Errore durante il caricamento da %s: %s",
                file_path,
                error,
            )


if __name__ == "__main__":
    # Configurazione base del logger
    logging.basicConfig(level=logging.INFO)

    logger.info("Inizio procedura di popolamento database...")
    seed_words_from_file("data/parole_it.txt", "IT")
    seed_words_from_file("data/parole_en.txt", "EN")
    logger.info("Procedura completata.")
