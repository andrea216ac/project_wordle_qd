"""Modulo per la finestra principale dell'applicazione Wordle."""

import os
import sys

# pylint: disable=no-member, c-extension-no-member, no-name-in-module
try:
    from PyQt6 import QtWidgets, uic

    HAS_QT = True
    BaseClass = QtWidgets.QMainWindow
except ImportError:
    HAS_QT = False
    BaseClass = object


class MainWindow(BaseClass):  # pylint: disable=too-few-public-methods
    """Classe che gestisce l'interfaccia principale."""

    def __init__(self, nome_giocatore="Andrea"):
        if not HAS_QT:
            self.nome_giocatore = nome_giocatore
            return

        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "main_window.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            self.btn_exit.clicked.connect(self.close)
            self.lbl_welcome.setText(f"Bentornato/a, {nome_giocatore}!")


if __name__ == "__main__":
    if HAS_QT:
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        print("Errore: PyQt6 non è installato o l'ambiente non supporta la GUI.")
