"""Modulo per la finestra principale dell'applicazione Wordle."""

# pylint: disable=import-outside-toplevel, cyclic-import

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

    def __init__(
        self,
        nome_giocatore: str = "Andrea",
        game_manager=None,
        modalita: str = "classic",
        lingua: str = "it",
    ):
        if not HAS_QT:
            self.nome_giocatore = nome_giocatore
            return

        super().__init__()

        self.logout_richiesto = False

        self.leaderboard_window = None
        self.game_window = None
        self.game_manager = game_manager
        self.nome_giocatore = nome_giocatore
        self.modalita = modalita
        self.lingua = lingua

        ui_path = os.path.join(os.path.dirname(__file__), "main_window.ui")

        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)

            btn_exit = getattr(self, "btn_exit", None)
            if btn_exit:
                btn_exit.clicked.connect(self.esegui_logout)

            lbl_welcome = getattr(self, "lbl_welcome", None)
            if lbl_welcome:
                lbl_welcome.setText(f"Bentornato/a, {nome_giocatore}!")

            btn_leaderboard = getattr(self, "btn_leaderboard", None)
            if btn_leaderboard:
                btn_leaderboard.clicked.connect(self.apri_classifica)

            btn_new_game = getattr(self, "btn_play", None)
            if btn_new_game:
                btn_new_game.clicked.connect(self.apri_nuova_partita)

            btn_training = getattr(self, "btn_training", None)
            if btn_training:
                btn_training.clicked.connect(self.apri_allenamento)

            if self.game_manager and btn_new_game:
                if self.game_manager.has_played_classic_today(self.nome_giocatore):
                    btn_new_game.setEnabled(False)
                    btn_new_game.setText("Già giocato")
                    btn_new_game.setStyleSheet("""
                        QPushButton { 
                            background-color: #3a3a3c; 
                            color: #818384; 
                            border: 1px solid #565758;
                        }
                    """)
        else:
            print(f"ERRORE: File UI non trovato in {ui_path}")

    def esegui_logout(self):
        """
        Imposta il flag di logout e chiude la finestra.
        Il ciclo nel main.py intercetterà questo flag e riaprirà il Login.
        """
        self.logout_richiesto = True
        self.close()

    def apri_classifica(self):
        """Metodo per aprire la finestra della classifica."""
        from src.gui.leaderboard_window import LeaderboardWindow

        if self.leaderboard_window is None:
            self.leaderboard_window = LeaderboardWindow(
                main_window=self, game_manager=self.game_manager
            )

        self.leaderboard_window.show()
        self.leaderboard_window.raise_()
        self.leaderboard_window.activateWindow()
        self.close()

    def apri_allenamento(self):
        """Metodo per aprire la finestra di allenamento."""
        self._avvia_gioco(modalita_scelta="training")

    def apri_nuova_partita(self):
        """Metodo per aprire la finestra di nuova partita."""
        self._avvia_gioco(modalita_scelta="classic")

    def _avvia_gioco(self, modalita_scelta):
        """Metodo usato per aprire la finestra di gioco."""
        from src.gui.game_window import GameWindow

        try:
            self.game_window = GameWindow(
                self,
                self.nome_giocatore,
                game_manager=self.game_manager,
                modalita=modalita_scelta,
                lingua=self.lingua,
            )

            self.game_window.show()
            self.game_window.raise_()
            self.game_window.activateWindow()
            self.close()

        except RuntimeError as e:
            QtWidgets.QMessageBox.warning(self, "Limite raggiunto", str(e))
            if modalita_scelta == "classic":
                btn_play = getattr(self, "btn_play", None)
                if btn_play:
                    btn_play.setEnabled(False)
                    btn_play.setText("Già giocato")


if __name__ == "__main__":
    if HAS_QT:
        app = QtWidgets.QApplication(sys.argv)
        # Mock per test rapido
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
