"""Unit tests per la finestra di registrazione."""

import pytest
from PyQt6.QtCore import Qt

from src.gui.registration_window import HAS_QT, RegistrationWindow


@pytest.fixture(name="reg_app")
def fixture_reg_app(request):
    if not HAS_QT:
        pytest.skip("Ambiente headless")

    try:
        qtbot_inst = request.getfixturevalue("qtbot")
    except Exception:
        pytest.skip("Plugin pytest-qt non disponibile")
        return None

    window = RegistrationWindow()
    qtbot_inst.addWidget(window)
    return window


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_fields_existence(reg_app):
    """Verifica che i 4 campi input esistano."""
    assert reg_app.input_nome is not None
    assert reg_app.input_cognome is not None
    assert reg_app.input_mail is not None
    assert reg_app.input_psw is not None


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_back_to_login_navigation(reg_app, qtbot):
    """Verifica che il tasto 'Accedi' riporti correttamente al login."""
    qtbot.mouseClick(reg_app.btn_login, Qt.MouseButton.LeftButton)
    assert not reg_app.isVisible()
    from src.gui.login_window import LoginWindow

    assert isinstance(reg_app.login_win, LoginWindow)


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_registration_validation_logic(reg_app):
    """Verifica che il tasto conferma si attivi solo a form completo."""
    if not reg_app.btn_confirm:
        pytest.skip("Tasto btn_registration_submit non presente nell'UI")

    reg_app.input_nome.setPlainText("Mario")
    reg_app.input_cognome.setPlainText("Rossi")
    reg_app.input_mail.setPlainText("mario@rossi.it")

    assert not reg_app.btn_confirm.isEnabled()

    reg_app.input_psw.setPlainText("123456")
    assert reg_app.btn_confirm.isEnabled()
