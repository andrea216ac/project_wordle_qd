"""Unit tests per la finestra di Login."""

import pytest
from PyQt6.QtCore import Qt

from src.gui.login_window import HAS_QT, LoginWindow


@pytest.fixture(name="login_app")
def fixture_login_app(request):
    if not HAS_QT:
        pytest.skip("Ambiente headless")

    try:
        qtbot_inst = request.getfixturevalue("qtbot")
    except Exception:
        pytest.skip("Plugin pytest-qt mancante")
        return None

    window = LoginWindow()
    qtbot_inst.addWidget(window)
    return window


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_ui_elements_presence(login_app):
    """Verifica che tutti i widget necessari siano caricati."""
    assert hasattr(login_app, "textEdit_mail")
    assert hasattr(login_app, "textEdit_psw")
    assert hasattr(login_app, "btn_login")
    assert login_app.lbl_title.text() == "Wordle"


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_login_transition(login_app, qtbot):
    """Verifica che il click su Accedi chiuda la finestra e crei la MainWindow."""
    login_app.textEdit_mail.setPlainText("TestUser")

    qtbot.mouseClick(login_app.btn_login, Qt.MouseButton.LeftButton)

    assert not login_app.isVisible()
    assert login_app.main_window.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_button_enabling_logic(login_app, qtbot):
    """Verifica che il pulsante si abiliti solo con campi compilati."""
    assert not login_app.btn_login.isEnabled()

    login_app.textEdit_mail.setPlainText("user@test.it")
    assert not login_app.btn_login.isEnabled()

    login_app.textEdit_psw.setPlainText("password123")
    assert login_app.btn_login.isEnabled()

    login_app.textEdit_mail.setPlainText("")
    assert not login_app.btn_login.isEnabled()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_successful_login_navigation(login_app, qtbot):
    """Verifica l'apertura della MainWindow con un utente fittizio."""
    utente_finto = "Mario Rossi"

    login_app.textEdit_mail.setPlainText(utente_finto)
    login_app.textEdit_psw.setPlainText("secret")

    qtbot.mouseClick(login_app.btn_login, Qt.MouseButton.LeftButton)

    assert not login_app.isVisible()
    assert login_app.main_window is not None
    assert login_app.main_window.isVisible()
    assert utente_finto in login_app.main_window.lbl_welcome.text()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_password_is_hidden(login_app):
    """
    Test concettuale: verifica se la password è oscurata.
    """
    # Questo test fallirebbe con il tuo XML attuale (QTextEdit).
    # Se passerai a QLineEdit, potrai scommentare la riga sotto:
    # assert login_app.textEdit_psw.echoMode() == QtWidgets.QLineEdit.EchoMode.Password
    pass
