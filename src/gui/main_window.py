"""Modulo per la finestra principale dell'applicazione Wordle."""

import os
import sys
from typing import Any, Type, cast

# pylint: disable=no-member, c-extension-no-member, no-name-in-module
try:
    from PyQt6 import QtWidgets, uic

    HAS_QT = True
    BaseClass: Type[Any] = QtWidgets.QMainWindow
except ImportError as e:
    print(f"ATTENZIONE: Errore caricamento Qt: {e}")
    HAS_QT = False
    BaseClass = cast(Type[Any], object)


class MainWindow(BaseClass):  # pylint: disable=too-few-public-methods
    """Classe che gestisce l'interfaccia principale."""

    def __init__(self, nome_giocatore: str = "Andrea", game_manager=None):
        if not HAS_QT:
            self.nome_giocatore = nome_giocatore
            return

        super().__init__()
        self.leaderboard_window = None
        self.game_window = None
        self.game_manager = game_manager

        ui_path = os.path.join(os.path.dirname(__file__), "main_window.ui")

        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)

            btn_exit = getattr(self, "btn_exit", None)
            if btn_exit:
                btn_exit.clicked.connect(self.close)

            lbl_welcome = getattr(self, "lbl_welcome", None)
            if lbl_welcome:
                lbl_welcome.setText(f"Bentornato/a, {nome_giocatore}!")

            btn_leaderboard = getattr(self, "btn_leaderboard", None)
            if btn_leaderboard:
                btn_leaderboard.clicked.connect(self.apri_classifica)

            btn_new_game = getattr(self, "btn_play", None)
            if btn_new_game:
                btn_new_game.clicked.connect(self.apri_nuova_partita)

        else:
            print(f"ERRORE: File UI non trovato in {ui_path}")

    def apri_classifica(self):
        """Metodo per aprire la finestra della classifica."""
        # pylint: disable=import-outside-toplevel
        from src.gui.leaderboard_window import LeaderboardWindow

        if self.leaderboard_window is None:
            self.leaderboard_window = LeaderboardWindow()

        self.leaderboard_window.show()
        self.leaderboard_window.raise_()
        self.leaderboard_window.activateWindow()

        self.close()

    def apri_nuova_partita(self):
        """Metodo per aprire la finestra del gioco."""
        # pylint: disable=import-outside-toplevel
        from src.gui.game_window import GameWindow

        self.game_window = GameWindow(
            main_window=self,
            game_manager=self.game_manager,
            nome_giocatore=self.nome_utente,
        )

        self.game_window.show()
        self.game_window.raise_()
        self.game_window.activateWindow()

        self.close()


if __name__ == "__main__":
    if HAS_QT:
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("Finestra avviata correttamente.")
        sys.exit(app.exec())
    else:
        print("Impossibile avviare l'interfaccia: PyQt6 non è configurato.")
