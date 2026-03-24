# pylint: disable=duplicate-code
"""Unit tests per la finestra di Registrazione."""

import pytest
from PyQt6.QtCore import Qt  # pylint: disable=no-name-in-module

from src.gui.registration_window import HAS_QT, RegistrationWindow


@pytest.fixture(name="registration_app")
def fixture_registration_app(qtbot):
    """Inizializza la finestra della registration window per i test UI."""
    if not HAS_QT:
        pytest.skip("Ambiente senza interfaccia grafica (headless)")

    window = RegistrationWindow()
    qtbot.addWidget(window)
    return window


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_ui_elements_presence(registration_app):
    """Verifica che tutti i widget necessari siano caricati."""
    assert hasattr(registration_app, "lineEdit_nome")
    assert hasattr(registration_app, "lineEdit_cognome")
    assert hasattr(registration_app, "lineEdit_username")
    assert hasattr(registration_app, "btn_registration_submit")
    assert hasattr(registration_app, "btn_login")


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_registration_transition(registration_app, qtbot):
    """Verifica che il click su Registrati chiuda la finestra e crei la MainWindow."""
    registration_app.lineEdit_nome.setText("Mario")
    registration_app.lineEdit_cognome.setText("Rossi")
    registration_app.lineEdit_username.setText("TestUser")

    qtbot.mouseClick(
        registration_app.btn_registration_submit, Qt.MouseButton.LeftButton
    )

    assert not registration_app.isVisible()
    assert registration_app.main_win.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_button_enabling_and_cursor_logic(registration_app):
    """Verifica l'abilitazione del pulsante e il cambio del cursore in base a tutti i campi."""
    assert not registration_app.btn_registration_submit.isEnabled()
    assert (
        registration_app.btn_registration_submit.cursor().shape()
        == Qt.CursorShape.ArrowCursor
    )

    registration_app.lineEdit_nome.setText("Mario")
    assert not registration_app.btn_registration_submit.isEnabled()

    registration_app.lineEdit_cognome.setText("Rossi")
    assert not registration_app.btn_registration_submit.isEnabled()

    registration_app.lineEdit_username.setText("Mario89")
    assert registration_app.btn_registration_submit.isEnabled()
    assert (
        registration_app.btn_registration_submit.cursor().shape()
        == Qt.CursorShape.PointingHandCursor
    )

    registration_app.lineEdit_username.setText("")
    assert not registration_app.btn_registration_submit.isEnabled()
    assert (
        registration_app.btn_registration_submit.cursor().shape()
        == Qt.CursorShape.ArrowCursor
    )


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_successful_registration_navigation(registration_app, qtbot):
    """Verifica l'apertura della MainWindow con il nome utente corretto dopo la registrazione."""
    utente_finto = "MarioRossi"

    qtbot.keyClicks(registration_app.lineEdit_nome, "Mario")
    qtbot.keyClicks(registration_app.lineEdit_cognome, "Rossi")
    qtbot.keyClicks(registration_app.lineEdit_username, utente_finto)

    qtbot.mouseClick(
        registration_app.btn_registration_submit, Qt.MouseButton.LeftButton
    )

    assert not registration_app.isVisible()
    assert registration_app.main_win is not None
    assert registration_app.main_win.isVisible()
    if hasattr(registration_app.main_win, "lbl_welcome"):
        assert utente_finto in registration_app.main_win.lbl_welcome.text()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_back_to_login_transition(registration_app, qtbot):
    """Verifica che il click su Accedi chiuda la registrazione e apra la LoginWindow."""
    assert not hasattr(registration_app, "log_win")

    qtbot.mouseClick(registration_app.btn_login, Qt.MouseButton.LeftButton)

    assert not registration_app.isVisible()
    assert registration_app.log_win is not None
    assert registration_app.log_win.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_whitespace_username_handling(registration_app):
    """Verifica che campi con soli spazi non abilitino la registrazione."""
    registration_app.lineEdit_nome.setText("Mario")
    registration_app.lineEdit_cognome.setText("Rossi")
    registration_app.lineEdit_username.setText("   ")

    assert not registration_app.btn_registration_submit.isEnabled()
    assert (
        registration_app.btn_registration_submit.cursor().shape()
        == Qt.CursorShape.ArrowCursor
    )


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_initial_ui_state(registration_app):
    """Verifica lo stato di default all'apertura della finestra."""
    assert registration_app.lineEdit_nome.text() == ""
    assert registration_app.lineEdit_cognome.text() == ""
    assert registration_app.lineEdit_username.text() == ""
    assert not registration_app.btn_registration_submit.isEnabled()
    assert (
        registration_app.btn_login.cursor().shape() == Qt.CursorShape.PointingHandCursor
    )


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_duplicate_username_error_visibility(registration_app, qtbot):
    """Verifica che l'errore appaia se l'username è già nel sistema."""

    window = registration_app
    window.show()

    qtbot.keyClicks(window.lineEdit_nome, "Andrea")
    qtbot.keyClicks(window.lineEdit_cognome, "Rossi")

    username_duplicato = "mario88"
    qtbot.keyClicks(window.lineEdit_username, username_duplicato)

    assert window.lbl_error_username.isVisible() is False

    qtbot.mouseClick(window.btn_registration_submit, Qt.MouseButton.LeftButton)

    assert window.lbl_error_username.isVisible() is True
    assert window.lbl_error_username.text() == "nome utente già usato"


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_error_hides_on_new_typing(registration_app, qtbot):
    """Verifica che l'errore sparisca quando l'utente ricomincia a scrivere."""
    window = registration_app
    window.lbl_error_username.show()

    qtbot.keyClick(window.lineEdit_username, Qt.Key.Key_Backspace)
    assert window.lbl_error_username.isVisible() is False
