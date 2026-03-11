"""Modulo per la finestra di Login dell'applicazione Wordle."""

import os
import sys
from typing import Any, Type

# pylint: disable=no-name-in-module, no-member, c-extension-no-member
try:
    from PyQt6 import QtWidgets, uic

    HAS_QT = True
    BaseDialog: Type[Any] = QtWidgets.QDialog
except ImportError:
    HAS_QT = False
    BaseDialog = object


class LoginWindow(BaseDialog):
    """Classe che gestisce il login dell'utente."""

    def __init__(self):
        """Inizializza la finestra di login."""
        super().__init__()

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

            if hasattr(self, "textEdit_mail"):
                self.textEdit_mail.textChanged.connect(self._controlla_campi)
            if hasattr(self, "textEdit_psw"):
                self.textEdit_psw.textChanged.connect(self._controlla_campi)

        if hasattr(self, "btn_registration"):
            self.btn_registration.clicked.connect(self.vai_a_registrazione)

    def _controlla_campi(self):
        """Abilita btn_login solo se mail e password non sono vuote."""
        mail = self.textEdit_mail.toPlainText().strip()
        psw = self.textEdit_psw.toPlainText().strip()

        self.btn_login.setEnabled(len(mail) > 0 and len(psw) > 0)

    def gestisci_accedi(self):
        """Logica per l'accesso e apertura della MainWindow."""
        email = self.textEdit_mail.toPlainText().strip()

        if not email:
            email = "Ospite"

        # pylint: disable=import-outside-toplevel
        from src.gui.main_window import MainWindow

        self.main_window = MainWindow(nome_giocatore=email)
        self.main_window.show()
        self.close()

    def vai_a_registrazione(self):
        """Metodo per aprire la finestra di registrazione."""
        print("Apertura pagina registrazione...")
        from src.gui.registration_window import RegistrationWindow

        self.reg_window = RegistrationWindow()
        self.reg_window.show()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
