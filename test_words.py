"""Script temporaneo per testare l'inserimento e l'estrazione delle parole."""

import datetime

from src.database.db import SessionLocal
from src.database.init_db import init_database
from src.database.models import Word
from src.database.word_repository import WordRepository


def run_test() -> None:
    """Esegue il test popolando il DB e stampando i risultati dell'estrazione."""
    # 1. Aggiorniamo il database per creare la nuova tabella 'words'
    init_database()

    with SessionLocal() as session:
        repo = WordRepository(session)

        # 2. Popoliamo il DB se è vuoto
        if session.query(Word).count() == 0:
            print("\n[DB] Popolamento iniziale del dizionario in corso...")
            parole_prova = [
                ("GATTO", "IT"),
                ("VOLPE", "IT"),
                ("TIGRE", "IT"),
                ("LEONE", "IT"),
                ("CERVO", "IT"),
                ("MOUSE", "EN"),
                ("HORSE", "EN"),
                ("SNAKE", "EN"),
            ]
            for parola, lingua in parole_prova:
                nuova_parola = Word(word=parola, language=lingua, length=5)
                session.add(nuova_parola)
            session.commit()
            print("[DB] Parole inserite con successo!\n")

        # 3. Test: Modalità Allenamento (Parole Casuali)
        print("--- TEST MODALITÀ ALLENAMENTO (IT) ---")
        for i in range(3):
            rnd = repo.get_random_word(language="IT", length=5)
            if rnd:
                print(f"Tentativo casuale {i+1}: {rnd.word}")

        # 4. Test: Modalità Sfida Giornaliera (Seed basato sulla data)
        print("\n--- TEST MODALITÀ GIORNALIERA (IT) ---")
        oggi = datetime.date.today()
        domani = oggi + datetime.timedelta(days=1)

        word_oggi_1 = repo.get_daily_word(target_date=oggi, language="IT", length=5)
        word_oggi_2 = repo.get_daily_word(target_date=oggi, language="IT", length=5)
        word_domani = repo.get_daily_word(target_date=domani, language="IT", length=5)

        if word_oggi_1 and word_oggi_2 and word_domani:
            print(f"Utente A gioca OGGI: ottiene '{word_oggi_1.word}'")
            print(
                f"Utente B gioca OGGI: ottiene '{word_oggi_2.word}' (DEVE essere identica!)"
            )
            print(f"Domani la parola cambierà e sarà: '{word_domani.word}'")


if __name__ == "__main__":
    run_test()
