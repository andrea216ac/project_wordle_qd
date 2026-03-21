"""Unit tests per la finestra di Login."""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt  # pylint: disable=no-name-in-module

from src.gui.login_window import HAS_QT, LoginWindow


@pytest.fixture(name="login_app")
def fixture_login_app(request):
    """Inizializza la finestra della login window per i test UI."""
    if not HAS_QT:
        pytest.skip("Ambiente headless")

    if "qtbot" not in request.fixturenames:
        pytest.skip("Plugin pytest-qt non installato o non configurato")
        return None

    qtbot_inst = request.getfixturevalue("qtbot")

    window = LoginWindow()
    qtbot_inst.addWidget(window)
    return window


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_ui_elements_presence(login_app):
    """Verifica che tutti i widget necessari siano caricati."""
    assert hasattr(login_app, "lineEdit_username")
    assert not hasattr(login_app, "textEdit_mail")
    assert hasattr(login_app, "btn_login")
    assert login_app.lbl_title.text() == "Wordle"


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_login_transition(login_app, qtbot):
    """Verifica che il click su Accedi chiuda la finestra e crei la MainWindow."""
    login_app.lineEdit_username.setText("TestUser")

    qtbot.mouseClick(login_app.btn_login, Qt.MouseButton.LeftButton)

    assert not login_app.isVisible()
    assert login_app.main_window.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_button_enabling_and_cursor_logic(login_app):
    """Verifica l'abilitazione del pulsante e il cambio del cursore."""
    assert not login_app.btn_login.isEnabled()
    assert login_app.btn_login.cursor().shape() == Qt.CursorShape.ArrowCursor

    login_app.lineEdit_username.setText("Mario")

    assert login_app.btn_login.isEnabled()
    assert login_app.btn_login.cursor().shape() == Qt.CursorShape.PointingHandCursor

    login_app.lineEdit_username.setText("")
    assert not login_app.btn_login.isEnabled()
    assert login_app.btn_login.cursor().shape() == Qt.CursorShape.ArrowCursor


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_successful_login_navigation(login_app, qtbot):
    """Verifica l'apertura della MainWindow con il nome utente corretto."""
    utente_finto = "MarioRossi"

    qtbot.keyClicks(login_app.lineEdit_username, utente_finto)

    qtbot.mouseClick(login_app.btn_login, Qt.MouseButton.LeftButton)

    assert not login_app.isVisible()
    assert login_app.main_window is not None
    assert login_app.main_window.isVisible()
    assert utente_finto in login_app.main_window.lbl_welcome.text()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_registration_transition(login_app, qtbot):
    """Verifica che il click su Registrati apra la RegistrationWindow."""
    assert login_app.reg_win is None

    qtbot.mouseClick(login_app.btn_registration, Qt.MouseButton.LeftButton)

    assert not login_app.isVisible()
    assert login_app.reg_win is not None
    assert login_app.reg_win.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_whitespace_username_handling(login_app):
    """Verifica che un nome utente di soli spazi non abiliti il login."""
    login_app.lineEdit_username.setText("   ")
    assert not login_app.btn_login.isEnabled()
    assert login_app.btn_login.cursor().shape() == Qt.CursorShape.ArrowCursor


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_initial_ui_state(login_app):
    """Verifica lo stato di default all'apertura della finestra."""
    assert login_app.lineEdit_username.text() == ""
    assert not login_app.btn_login.isEnabled()
    assert (
        login_app.btn_registration.cursor().shape() == Qt.CursorShape.PointingHandCursor
    )

def test_login_failed_user_not_found(login_app, qtbot):
    """Verifica che appaia l'errore se l'utente non esiste nel DB."""
    mock_session = MagicMock()
    mock_session.query().filter_by().first.return_value = None
    login_app.sessione_db = mock_session
    
    login_app.lineEdit_username.setText("Utente non trovato. Registrati per giocare.")
    
    login_app.lbl_error_login = MagicMock()
    
    qtbot.mouseClick(login_app.btn_login, Qt.MouseButton.LeftButton)

    login_app.lbl_error_login.show.assert_called()

def test_registration_cancelled(login_app, qtbot):
    """Verifica che se annullo la registrazione, la login torni visibile."""
    with patch("src.gui.registration_window.RegistrationWindow") as mock_reg_class:
        mock_reg_inst = mock_reg_class.return_value
        mock_reg_inst.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
        
        qtbot.mouseClick(login_app.btn_registration, Qt.MouseButton.LeftButton)

        assert login_app.isVisible()
