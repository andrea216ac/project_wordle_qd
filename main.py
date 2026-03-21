"""Punto di ingresso principale dell'applicazione Wordle."""

# pylint: disable=no-name-in-module, c-extension-no-member

import os
import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication

from src.core.game_manager import GameManager
from src.core.word_provider import WordProvider
from src.database.db import Base, SessionLocal, engine
from src.database.game_repository import GameRepository
from src.database.word_repository import WordRepository
from src.gui.login_window import LoginWindow
from src.gui.main_window import MainWindow


def main() -> None:
    """Inizializza ed esegue l'applicazione."""
    app = QApplication(sys.argv)

    user_settings = {
        "mode": "training" if "--debug" in sys.argv else "classic",
        "lang": "EN" if "--english" in sys.argv else "IT",
    }

    sessione_db = None
    exit_code = 0

    try:
        # Inizializzazione Database
        if not os.path.exists("wordle.db"):
            print("Inizializzazione database wordle.db in corso...")
        Base.metadata.create_all(bind=engine)

        sessione_db = SessionLocal()

        # Inizializziamo i componenti core UNA SOLA VOLTA fuori dal ciclo
        word_repo = WordRepository(session=sessione_db)
        game_repo = GameRepository(session=sessione_db)
        provider = WordProvider(word_repo)
        manager = GameManager(
            word_provider=provider,
            score_repository=game_repo,
        )

        # --- CICLO DELLE SESSIONI ---
        while True:
            # 1. Mostra la finestra di Login
            login = LoginWindow(sessione_db)
            login.game_manager = (
                manager  # Passiamo il manager per permettere la registrazione
            )

            # Se l'utente chiude la finestra di login (X), usciamo dal programma
            if login.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                break

            nome_effettivo = login.user_name
            manager.current_user = nome_effettivo
            # 2. Mostra la Main Window
            finestra_menu = MainWindow(
                nome_giocatore=nome_effettivo,
                game_manager=manager,
                modalita=user_settings["mode"],
                lingua=user_settings["lang"],
            )

            finestra_menu.show()

            # app.exec() ferma l'esecuzione qui finché finestra_menu non viene chiusa
            app.exec()

            # 3. Controllo Logout
            # Verifichiamo se finestra_menu è stata chiusa tramite il tasto Logout
            # (Assicurati che in MainWindow.esegui_logout tu imposti self.logout_richiesto = True)
            logout_richiesto = getattr(finestra_menu, "logout_richiesto", False)

            if not logout_richiesto:
                # Se la finestra è stata chiusa con la X, usciamo definitivamente
                break

            print(f"Sessione terminata per {nome_effettivo}. Ritorno al login...")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Errore fatale: {e}")
        exit_code = 1

    finally:
        if sessione_db:
            sessione_db.close()
            print("Sessione database chiusa correttamente.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()