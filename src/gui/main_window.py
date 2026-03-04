"""Modulo per la finestra principale dell'applicazione Wordle."""

import os
import sys

from PyQt6 import QtWidgets, uic # pylint: disable=no-member


class MainWindow(QtWidgets.QMainWindow): # pylint: disable=too-few-public-methods
    """Classe che gestisce l'interfaccia principale."""

    def __init__(self, nome_giocatore="Andrea"):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "main_window.ui")
        uic.loadUi(ui_path, self)
        self.btn_exit.clicked.connect(self.close)

        self.lbl_welcome.setText(f"Bentornato/a, {nome_giocatore}!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
