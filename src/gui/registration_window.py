import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    from PyQt6 import QtWidgets, uic
    from PyQt6.QtCore import Qt

    HAS_QT = True
except ImportError:
    HAS_QT = False


class RegistrationWindow(QtWidgets.QDialog):
    """Classe che gestisce la creazione di un nuovo account."""

    def __init__(self, parent=None):
        super().__init__(parent)
        if not HAS_QT:
            return

        ui_path = os.path.join(os.path.dirname(__file__), "registration_window.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            print(f"Errore: Il file {ui_path} non esiste!")

        self.input_nome = getattr(self, "lineEdit_nome", None)
        self.input_cognome = getattr(self, "lineEdit_cognome", None)
        self.input_username = getattr(self, "lineEdit_username", None)

        if self.lbl_error_username:
            self.lbl_error_username.hide()

        if self.input_username:
            self.input_username.textChanged.connect(
                lambda: self.lbl_error_username.hide()
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
            if valido:
                self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.btn_confirm.setCursor(Qt.CursorShape.ArrowCursor)

    def vai_a_login(self):
        """Chiude la registrazione e apre il Login."""
        try:
            from src.gui.login_window import LoginWindow

            self.log_win = LoginWindow()
            self.log_win.show()
            self.close()
        except ImportError as e:
            print(f"Errore nell'apertura del Login: {e}")

    def esegui_registrazione(self):
        """Effettua la registrazione e lancia la MainWindow."""
        username = self.input_username.text().strip()

        database_utenti_esistenti = ["mario88", "admin", "wordle_master"]

        if username.lower() in database_utenti_esistenti:
            if self.lbl_error_username:
                self.lbl_error_username.show()
            return

        print(f"Utente registrato: {username}")

        try:
            from src.gui.main_window import MainWindow

            self.main_win = MainWindow()

            if hasattr(self.main_win, "lbl_welcome"):
                self.main_win.lbl_welcome.setText(f"Benvenuto, {username}!")

            self.main_win.show()
            self.close()
        except ImportError as e:
            QtWidgets.QMessageBox.critical(
                self, "Errore di Sistema", f"MainWindow non trovata: {e}"
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec())
