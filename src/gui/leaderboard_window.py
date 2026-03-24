"""Modulo per la finestra della classifica dell'applicazione Wordle."""

# pylint: disable=import-outside-toplevel, cyclic-import

# pylint: disable=duplicate-code
import os
import sys
from typing import Any, Type

# pylint: disable=no-name-in-module, no-member, c-extension-no-member
try:
    from PyQt6 import QtWidgets, uic
    from PyQt6.QtWidgets import QHeaderView, QTableWidgetItem

    HAS_QT = True
    BaseDialog: Type[Any] = QtWidgets.QDialog
except ImportError:
    HAS_QT = False
    BaseDialog = object


class LeaderboardWindow(BaseDialog):
    """Classe che gestisce la visualizzazione della classifica utenti."""

    def __init__(self, main_window=None, game_manager=None):
        """Inizializza la finestra e carica i dati della classifica."""
        super().__init__()

        self.main_window = main_window
        self.game_manager = game_manager

        ui_path = os.path.join(os.path.dirname(__file__), "leaderboard_window.ui")

        if not os.path.exists(ui_path):
            print(f"Errore: Il file {ui_path} non esiste!")
            return

        uic.loadUi(ui_path, self)

        self.table_user_pos.setColumnCount(3)
        self.table_user_pos.setHorizontalHeaderLabels(
            ["Posizione", "Vittorie", "Media Tentativi"]
        )

        btn_back = getattr(self, "btn_back", None)
        if btn_back:
            btn_back.clicked.connect(self.torna_indietro)

        if hasattr(self, "table_top3") and hasattr(self, "table_user_pos"):
            self.setup_leaderboard_graphics()
            self.aggiorna_classifica()
        else:
            print("ERRORE: Tabelle non trovate nel file .ui. Verifica gli objectName.")

    def setup_leaderboard_graphics(self):
        """Configura le intestazioni e il comportamento delle tabelle."""
        self.table_top3.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )

        self.table_top3.setColumnCount(4)
        self.table_top3.setHorizontalHeaderLabels(
            ["Pos.", "Utente", "Vittorie", "Media Tentativi"]
        )
        self.table_top3.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_top3.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table_user_pos.setColumnCount(3)
        self.table_user_pos.setHorizontalHeaderLabels(
            ["Posizione", "Vittorie", "Media Tentativi"]
        )
        self.table_user_pos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_user_pos.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        style = """
            QTableWidget { background-color: #ffffff; gridline-color: #d3d6da; border-radius: 5px; }
            QHeaderView::section { background-color: #787c7e; color: white; font-weight: bold; }
            QTableWidget::item { color: #1a1a1a; }
        """
        self.table_top3.setStyleSheet(style)
        self.table_user_pos.setStyleSheet(style)

    def aggiorna_classifica(self):
        """Recupera i dati aggiornati tramite GameManager e popola la UI."""
        dati = []
        nome_utente = "Ospite"

        if self.game_manager:
            dati = self.game_manager.get_leaderboard()
            nome_utente = self.game_manager.get_current_user() or "Ospite"
        else:
            print("Attenzione: GameManager non passato alla LeaderboardWindow.")

        self.popola_classifica(dati, nome_utente)

    def popola_classifica(self, dati, nome_utente_corrente):
        """Inserisce i dati reali all'interno dei widget QTableWidget."""
        self.table_top3.setRowCount(min(3, len(dati)))
        for i in range(min(3, len(dati))):
            giocatore = dati[i]
            self.table_top3.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table_top3.setItem(i, 1, QTableWidgetItem(giocatore["utente"]))
            self.table_top3.setItem(i, 2, QTableWidgetItem(str(giocatore["vittorie"])))
            self.table_top3.setItem(i, 3, QTableWidgetItem(str(giocatore["media"])))

        pos_utente = -1
        dati_utente = None
        for index, g in enumerate(dati):
            if g["utente"].lower() == nome_utente_corrente.lower():
                pos_utente = index + 1
                dati_utente = g
                break

        if dati_utente:
            self.table_user_pos.setRowCount(1)
            self.table_user_pos.setItem(0, 0, QTableWidgetItem(f"{pos_utente}°"))
            self.table_user_pos.setItem(
                0, 1, QTableWidgetItem(str(dati_utente["vittorie"]))
            )
            self.table_user_pos.setItem(
                0, 2, QTableWidgetItem(str(dati_utente["media"]))
            )
        else:
            self.table_user_pos.setRowCount(0)

    def torna_indietro(self):
        """Metodo per tornare alla main window evitando crash se il manager è None."""
        from src.gui.main_window import MainWindow

        username = "Ospite"
        if self.game_manager is not None:
            username = self.game_manager.get_current_user() or "Ospite"

        if self.main_window is None:
            self.main_window = MainWindow(
                nome_giocatore=username, game_manager=self.game_manager
            )

        self.main_window.show()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LeaderboardWindow()
    window.show()
    sys.exit(app.exec())
