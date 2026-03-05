"""Modulo per la finestra principale dell'applicazione Wordle."""

import os
import sys
from typing import Any, Type  # Aggiungi questa riga

# pylint: disable=no-member, c-extension-no-member, no-name-in-module
try:
    from PyQt6 import QtWidgets, uic
    HAS_QT = True
    BaseClass: Type[Any] = QtWidgets.QMainWindow
except ImportError:
    HAS_QT = False
    BaseClass = object


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
