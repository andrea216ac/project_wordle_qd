import os
import sys

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QHeaderView, QTableWidgetItem


class LeaderboardWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), "leaderboard_window.ui")

        if not os.path.exists(ui_path):
            print(f"Errore: Il file {ui_path} non esiste!")
            return

        uic.loadUi(ui_path, self)

        self.dati_classifica = [
            {"utente": "Andrea", "media": 3.2, "vittorie": 45},
            {"utente": "Luca", "media": 3.8, "vittorie": 38},
            {"utente": "Sara", "media": 4.1, "vittorie": 30},
            {"utente": "Tu (Esempio)", "media": 4.5, "vittorie": 12},
        ]

        if hasattr(self, "table_top3") and hasattr(self, "table_user_pos"):
            self.setup_leaderboard_graphics()
            self.popola_classifica(
                self.dati_classifica, nome_utente_corrente="Tu (Esempio)"
            )
        else:
            print(
                "ERRORE: I nomi 'table_top3' o 'table_user_pos' non corrispondono all'objectName nel file .ui"
            )

    def setup_leaderboard_graphics(self):
        self.table_top3.setColumnCount(4)
        self.table_top3.setHorizontalHeaderLabels(
            ["Pos.", "Utente", "Media Tentativi", "Vittorie"]
        )
        self.table_top3.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_top3.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table_user_pos.setColumnCount(3)
        self.table_user_pos.setHorizontalHeaderLabels(
            ["Pos.", "Media Tentativi", "Vittorie"]
        )
        self.table_user_pos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_user_pos.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

    def popola_classifica(self, dati, nome_utente_corrente):
        dati_ordinati = sorted(dati, key=lambda x: (-x["vittorie"], x["media"]))

        self.table_top3.setRowCount(3)
        for i in range(min(3, len(dati_ordinati))):
            giocatore = dati_ordinati[i]
            self.table_top3.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table_top3.setItem(i, 1, QTableWidgetItem(giocatore["utente"]))
            self.table_top3.setItem(i, 2, QTableWidgetItem(str(giocatore["media"])))
            self.table_top3.setItem(i, 3, QTableWidgetItem(str(giocatore["vittorie"])))

        pos_utente = -1
        dati_utente = None
        for index, g in enumerate(dati_ordinati):
            if g["utente"] == nome_utente_corrente:
                pos_utente = index + 1
                dati_utente = g
                break

        if dati_utente:
            self.table_user_pos.setRowCount(1)
            self.table_user_pos.setItem(0, 0, QTableWidgetItem(str(pos_utente)))
            self.table_user_pos.setItem(
                0, 1, QTableWidgetItem(str(dati_utente["media"]))
            )
            self.table_user_pos.setItem(
                0, 2, QTableWidgetItem(str(dati_utente["vittorie"]))
            )

        style = """
            QTableWidget { background-color: #ffffff; gridline-color: #d3d6da; border: none; }
            QHeaderView::section { background-color: #787c7e; color: white; padding: 5px; font-weight: bold; }
            QTableWidget::item { padding: 10px; color: #1a1a1a; }
        """
        self.table_top3.setStyleSheet(style)
        self.table_user_pos.setStyleSheet(style)


# --- BLOCCO DI ESECUZIONE ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LeaderboardWindow()
    window.show()
    sys.exit(app.exec())
