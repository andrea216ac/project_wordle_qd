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

    def __init__(self, nome_giocatore: str = "Andrea"):
        if not HAS_QT:
            self.nome_giocatore = nome_giocatore
            return

        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "main_window.ui")

        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)

            btn_exit = getattr(self, "btn_exit", None)
            if btn_exit:
                btn_exit.clicked.connect(self.close)

            lbl_welcome = getattr(self, "lbl_welcome", None)
            if lbl_welcome:
                lbl_welcome.setText(f"Bentornato/a, {nome_giocatore}!")
        else:
            print(f"ERRORE: File UI non trovato in {ui_path}")


if __name__ == "__main__":
    if HAS_QT:
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("Finestra avviata correttamente.")
        sys.exit(app.exec())
    else:
        print("Impossibile avviare l'interfaccia: PyQt6 non è configurato.")
