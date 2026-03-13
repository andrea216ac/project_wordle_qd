"""Modulo per la finestra di registrazione dell'applicazione Wordle."""

import os
import sys
from typing import Any, Type

# pylint: disable=no-name-in-module, no-member, c-extension-no-member
try:
    from PyQt6 import QtCore, QtWidgets, uic

    HAS_QT = True
    BaseDialog: Type[Any] = QtWidgets.QDialog
    _signal_factory: Any = QtCore.pyqtSignal
except ImportError:
    HAS_QT = False
    BaseDialog = object

    def _mock_signal(*_args: Any, **_kwargs: Any) -> Any:
        """Mock del segnale per ambiente senza Qt."""
        return object()

    _signal_factory = _mock_signal  # type: ignore[assignment]

pyqt_signal = _signal_factory


class RegistrationWindow(BaseDialog):
    """Classe che gestisce la creazione di un nuovo account."""

    ritorno_al_login = pyqt_signal()

    def __init__(self):
        """Inizializza la finestra di registrazione."""
        super().__init__()
        self.login_win = None
        if not HAS_QT:
            return

        ui_path = os.path.join(os.path.dirname(__file__), "registration_window.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            print(f"Errore: Il file {ui_path} non esiste!")

        self.input_nome = getattr(self, "textEdit", None)
        self.input_cognome = getattr(self, "textEdit_2", None)
        self.input_mail = getattr(self, "textEdit_3", None)
        self.input_psw = getattr(self, "textEdit_4", None)

        if hasattr(self, "btn_login"):
            self.btn_login.clicked.connect(self.vai_a_login)

        self.btn_confirm = getattr(self, "btn_registration_submit", None)
        if self.btn_confirm:
            self.btn_confirm.setEnabled(False)
            self.btn_confirm.clicked.connect(self.esegui_registrazione)

        self.campi_obbligatori = [
            self.input_nome,
            self.input_cognome,
            self.input_mail,
            self.input_psw,
        ]

        for field in self.campi_obbligatori:
            if field:
                field.textChanged.connect(self.valida_form)

    def valida_form(self):
        """Abilita il tasto conferma solo se tutti i campi sono pieni e validi."""
        if not self.btn_confirm:
            return

        stato_campi = []
        for field in self.campi_obbligatori:
            if field:
                testo = field.toPlainText().strip()
                stato_campi.append(len(testo) > 0)
            else:
                stato_campi.append(False)

        form_valido = all(stato_campi)
        self.btn_confirm.setEnabled(form_valido)

    def vai_a_login(self):
        """Torna alla finestra di login."""
        self.ritorno_al_login.emit()
        self.close()

    def esegui_registrazione(self):
        """Logica per salvare l'utente e mandarlo al login."""
        nome = self.input_nome.toPlainText().strip()
        print(f"Registrazione di: {nome}")
        self.vai_a_login()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec())
