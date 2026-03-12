from typing import Any, cast
from unittest.mock import MagicMock

import pytest

# pylint: disable=no-name-in-module, disable=protected-access, redefined-outer-name, duplicate-code
try:
    from PyQt6 import QtWidgets as real_widgets
    from PyQt6.QtCore import Qt as real_qt
    
    QtWidgets = cast(Any, real_widgets)
    Qt = cast(Any, real_qt)
    HAS_QT = True
except ImportError:
    QtWidgets = cast(Any, MagicMock())
    Qt = cast(Any, MagicMock())
    HAS_QT = False

from src.gui.game_window import GameWindow


@pytest.fixture()
def game_instance(request):
    """Fixture per inizializzare la finestra prima di ogni test."""
    if not HAS_QT:
        pytest.skip("Ambiente headless")

    if "qtbot" not in request.fixturenames:
        pytest.skip("Plugin pytest-qt non installato o non configurato")
        return None

    qtbot_inst = request.getfixturevalue("qtbot")

    window = GameWindow("TestPlayer")
    qtbot_inst.addWidget(window)
    return window


def test_initial_state(app):
    """Verifica che all'avvio solo la prima cella sia abilitata."""
    assert app.current_row == 0
    assert app.current_col == 0
    assert app.grid[0][0].isEnabled() is True
    assert app.grid[0][1].isEnabled() is False


def test_typing_moves_cursor(app):
    """Verifica che scrivendo una lettera il cursore si sposti a destra."""
    app._ui_on_key_press("A")
    assert app.current_col == 1
    assert app.grid[0][0].toPlainText() == "A"
    assert app.grid[0][1].isEnabled() is True


def test_backspace_logic(app):
    """Verifica che il backspace cancelli la lettera e torni indietro."""
    app._ui_on_key_press("W")
    app._ui_on_backspace()
    assert app.current_col == 0
    assert app.grid[0][0].toPlainText() == ""


def test_cannot_enter_short_word(app):
    """Verifica che premendo INVIO su una riga incompleta non si passi alla successiva."""
    app._ui_on_key_press("T")
    app._ui_on_enter()
    assert app.current_row == 0


def test_row_progression(app):
    """Verifica il passaggio alla riga successiva dopo una parola completa."""
    for char in "HELLO":
        app._ui_on_key_press(char)

    app._ui_on_enter()

    assert app.current_row == 1
    assert app.current_col == 0
    assert app.grid[1][0].isEnabled() is True
    assert app.grid[0][0].isEnabled() is False


def test_keyboard_buttons_exist(app):
    """Verifica che la tastiera QWERTY sia stata generata nel container."""
    buttons = app.keyboard_container.findChildren(QtWidgets.QPushButton)
    assert len(buttons) >= 28
