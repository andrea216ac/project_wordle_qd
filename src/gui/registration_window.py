# pylint: disable=no-member, c-extension-no-member, too-many-instance-attributes
"""Modulo per la finestra di registrazione di Wordle."""

import os
import sys
from typing import Any, Type

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    from PyQt6 import QtWidgets, uic
    from PyQt6.QtCore import Qt

    HAS_QT = True
    BaseDialog: Type[Any] = QtWidgets.QDialog
except ImportError:
    HAS_QT = False
    BaseDialog = object


class RegistrationWindow(BaseDialog):
    """Classe che gestisce la creazione di un nuovo account."""

    def __init__(self, sessione_db=None, game_manager=None, parent=None):
        if not HAS_QT:
            super().__init__()
            return

        super().__init__(parent)
        self.sessione_db = sessione_db
        self.game_manager = game_manager
        self.log_win = None
        self.main_win = None

        ui_path = os.path.join(os.path.dirname(__file__), "registration_window.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            print(f"Errore: Il file {ui_path} non esiste!")

        self.input_nome = getattr(self, "lineEdit_nome", None)
        self.input_cognome = getattr(self, "lineEdit_cognome", None)
        self.input_username = getattr(self, "lineEdit_username", None)
        self.lbl_error_username = getattr(self, "lbl_error_username", None)

        if self.lbl_error_username:
            self.lbl_error_username.hide()

        if self.input_username:
            # pylint: disable=unnecessary-lambda
            self.input_username.textChanged.connect(
                lambda: (
                    self.lbl_error_username.hide() if self.lbl_error_username else None
                )
            )

        self.btn_confirm = getattr(self, "btn_registration_submit", None)
        self.btn_back_to_login = getattr(self, "btn_login", None)

        if self.btn_confirm:
            self.btn_confirm.setEnabled(False)
            self.btn_confirm.setCursor(Qt.CursorShape.ArrowCursor)
            self.btn_confirm.clicked.connect(self.esegui_registrazione)

        if self.btn_back_to_login:
            self.btn_back_to_login.clicked.connect(self.vai_a_login)

        self.campi = [self.input_nome, self.input_cognome, self.input_username]
        for f in self.campi:
            if f:
                f.textChanged.connect(self.valida_form)

    def valida_form(self):
        """Abilita il tasto e cambia il cursore solo se il form è completo."""
        valido = all(f.text().strip() != "" for f in self.campi if f)

        if self.btn_confirm:
            self.btn_confirm.setEnabled(valido)
            cursor = (
                Qt.CursorShape.PointingHandCursor
                if valido
                else Qt.CursorShape.ArrowCursor
            )
            self.btn_confirm.setCursor(cursor)

    def vai_a_login(self):
        """Chiude la registrazione e apre il Login."""
        try:
            # pylint: disable=import-outside-toplevel, cyclic-import
            from src.gui.login_window import LoginWindow

            self.log_win = LoginWindow(
                sessione_db=self.sessione_db,
                game_manager=getattr(self, "game_manager", None),
            )
            self.log_win.show()
            self.hide()
            if self.log_win.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.user_name = self.log_win.user_name
                self.accept()
            else:
                self.show()
        except ImportError as e:
            print(f"Errore nell'apertura del Login: {e}")

    def esegui_registrazione(self):
        """Effettua la registrazione e chiude il dialogo con successo."""
        username = self.input_username.text().strip()

        if self.sessione_db:
            from src.database.models import User

            utente_esiste = (
                self.sessione_db.query(User).filter_by(username=username).first()
            )

            if utente_esiste:
                if self.lbl_error_username:
                    self.lbl_error_username.show()
                return

            try:
                nuovo_utente = User(username=username)
                self.sessione_db.add(nuovo_utente)
                self.sessione_db.commit()
            except Exception as e:
                self.sessione_db.rollback()
                print(f"Errore durante il salvataggio: {e}")
                return

        self.user_name = username

        self.accept()


if __name__ == "__main__":
    if HAS_QT:
        app = QtWidgets.QApplication(sys.argv)
        window = RegistrationWindow()
        window.show()
        sys.exit(app.exec())
