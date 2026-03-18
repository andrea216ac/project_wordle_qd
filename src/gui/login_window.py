# pylint: disable=too-few-public-methods
"""Modulo per la finestra di Login dell'applicazione Wordle."""

# pylint: disable=duplicate-code
import os
import sys
from typing import Any, Type

# pylint: disable=no-name-in-module, no-member, c-extension-no-member
try:
    from PyQt6 import QtWidgets, uic
    from PyQt6.QtCore import Qt

    HAS_QT = True
    BaseDialog: Type[Any] = QtWidgets.QDialog
except ImportError:
    HAS_QT = False
    BaseDialog = object

    class _MockCursorShape:
        PointingHandCursor = 13
        ArrowCursor = 0

    class _MockQt:
        CursorShape = _MockCursorShape

    Qt = _MockQt  # type: ignore


class LoginWindow(QtWidgets.QDialog):
    """Classe che gestisce il login dell'utente."""

    def __init__(self, sessione_db=None, game_manager=None, parent=None):
        """Inizializza la finestra di login."""
        super().__init__(parent)

        self.sessione_db = sessione_db
        self.game_manager = game_manager
        self.user_name = None
        self.main_window = None
        self.reg_win = None

        if not HAS_QT:
            return

        ui_path = os.path.join(os.path.dirname(__file__), "login_window.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            print(f"Errore: Il file {ui_path} non esiste!")

        if hasattr(self, "btn_login"):
            self.btn_login.setEnabled(False)
            self.btn_login.clicked.connect(self.gestisci_accedi)

        if hasattr(self, "lbl_error_login"):
            self.lbl_error_login.hide()

        if hasattr(self, "lineEdit_username"):
            self.lineEdit_username.textChanged.connect(self._controlla_campi)

        if hasattr(self, "btn_registration"):
            self.btn_registration.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_registration.clicked.connect(self.vai_a_registrazione)

    def _controlla_campi(self):
        """Abilita btn_login e cambia il cursore se il nome utente non è vuoto."""
        username = self.lineEdit_username.text().strip()

        is_valid = len(username) > 0
        self.btn_login.setEnabled(is_valid)

        if is_valid:
            self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.btn_login.setCursor(Qt.CursorShape.ArrowCursor)

    def gestisci_accedi(self):
        """Logica per l'accesso e apertura della MainWindow."""
        # pylint: disable=import-outside-toplevel
        username = self.lineEdit_username.text().strip()

        if not username:
            return

        if self.sessione_db:
            from src.database.models import User

            utente = self.sessione_db.query(User).filter_by(username=username).first()
            if utente:
                # L'utente esiste, procediamo
                self.user_name = username
                self.accept()
            else:
                # L'utente NON esiste: mostriamo il messaggio di errore
                if hasattr(self, "lbl_error_login"):
                    self.lbl_error_login.show()

    def vai_a_registrazione(self):
        """Chiude il Login e apre la Registrazione."""
        # pylint: disable=import-outside-toplevel
        try:
            from src.gui.registration_window import RegistrationWindow

            self.reg_win = RegistrationWindow(
                sessione_db=self.sessione_db,
                game_manager=getattr(self, "game_manager", None),
            )
            self.reg_win.show()
            self.hide()

            if self.reg_win.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.user_name = self.reg_win.user_name
                self.accept()
            else:
                self.show()
        except ImportError as e:
            print(f"Errore nell'apertura del Registrazione: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
