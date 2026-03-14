"""Unit test per la finestra di gioco"""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest

# pylint: disable=no-name-in-module, duplicate-code, c-extension-no-member, invalid-name, protected-access, redefined-outer-name
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


@pytest.fixture(name="game")
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


def test_initial_state(game):
    """Verifica che all'avvio solo la prima cella sia abilitata."""
    assert game.current_row == 0
    assert game.current_col == 0
    assert game.grid[0][0].isEnabled() is True
    assert game.grid[0][1].isEnabled() is False


def test_typing_moves_cursor(game):
    """Verifica che scrivendo una lettera il cursore si sposti a destra."""
    game._ui_on_key_press("A")
    assert game.current_col == 1
    assert game.grid[0][0].toPlainText() == "A"
    assert game.grid[0][1].isEnabled() is True


def test_backspace_logic(game):
    """Verifica che il backspace cancelli la lettera e torni indietro."""
    game._ui_on_key_press("W")
    game._ui_on_backspace()
    assert game.current_col == 0
    assert game.grid[0][0].toPlainText() == ""


def test_cannot_enter_short_word(game):
    """Verifica che premendo INVIO su una riga incompleta non si passi alla successiva."""
    game._ui_on_key_press("T")
    game._ui_on_enter()
    assert game.current_row == 0


def test_row_progression(game):
    """Verifica il passaggio alla riga successiva dopo una parola completa."""
    for char in "HELLO":
        game._ui_on_key_press(char)

    game._ui_on_enter()

    assert game.current_row == 1
    assert game.current_col == 0
    assert game.grid[1][0].isEnabled() is True
    assert game.grid[0][0].isEnabled() is False


def test_keyboard_buttons_exist(game):
    """Verifica che la tastiera QWERTY sia stata generata nel container."""
    buttons = game.keyboard_container.findChildren(QtWidgets.QPushButton)
    assert len(buttons) >= 28


def test_exit_button_closes_window(game, qtbot):
    """Verifica che il tasto 'Esci' chiuda effettivamente la finestra."""
    btn_exit = game.pushButton

    assert btn_exit is not None
    assert btn_exit.text() == "Esci"

    qtbot.mouseClick(btn_exit, Qt.MouseButton.LeftButton)

    assert game.isHidden() is True


def test_row_limit(game, qtbot):
    """Verifica che non si possa andare oltre la sesta riga (6x5)."""
    game.current_row = 5

    for char in "WORLD":
        qtbot.keyClick(game, getattr(Qt.Key, f"Key_{char}"))

    qtbot.keyClick(game, Qt.Key.Key_Return)

    assert game.current_row == 5


def test_physical_keyboard_typing(game, qtbot):
    """Verifica che premendo tasti sulla tastiera fisica le lettere appaiano."""
    qtbot.keyClick(game, Qt.Key.Key_W)

    assert game.grid[0][0].toPlainText() == "W"
    assert game.current_col == 1


def test_physical_keyboard_backspace(game, qtbot):
    """Verifica che il backspace fisico cancelli correttamente."""
    qtbot.keyClick(game, Qt.Key.Key_X)
    assert game.grid[0][0].toPlainText() == "X"

    qtbot.keyClick(game, Qt.Key.Key_Backspace)
    assert game.grid[0][0].toPlainText() == ""
    assert game.current_col == 0


def test_physical_keyboard_enter_progression(game, qtbot):
    """Verifica che l'invio fisico faccia avanzare di riga se la parola è completa."""
    for char in "HELLO":
        qtbot.keyClick(game, getattr(Qt.Key, f"Key_{char}"))

    assert game.current_row == 0
    assert game.current_col == 4

    qtbot.keyClick(game, Qt.Key.Key_Return)

    assert game.current_row == 1
    assert game.current_col == 0


def test_physical_escape_closes_window(game, qtbot):
    """Verifica che il tasto ESC fisico chiuda la finestra."""
    qtbot.keyClick(game, Qt.Key.Key_Escape)
    assert game.isHidden() is True
