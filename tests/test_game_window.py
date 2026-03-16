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

    mock_manager = MagicMock()

    mock_manager.is_game_over.return_value = False
    mock_manager.submit_guess.return_value = ["Assente"] * 5
    mock_manager.get_attempts.return_value = 1

    window = GameWindow(nome_giocatore="TestPlayer", GameManager=mock_manager)

    qtbot_inst.addWidget(window)
    window.show()
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
    game.GameManager = MagicMock()
    game.GameManager.is_game_over.return_value = False
    game.GameManager.submit_guess.return_value = ["Assente"] * 5

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
    """Verifica che il tasto 'Esci' apra la main window."""
    btn_exit = game.btn_back

    assert btn_exit is not None
    assert btn_exit.text() == "Esci"

    qtbot.mouseClick(btn_exit, Qt.MouseButton.LeftButton)

    assert game.isHidden() is True
    assert game.main_window is not None


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
    game.GameManager = MagicMock()
    game.GameManager.is_game_over.return_value = False
    game.GameManager.submit_guess.return_value = ["Assente"] * 5

    for char in "HELLO":
        qtbot.keyClick(game, getattr(Qt.Key, f"Key_{char}"))

    assert game.current_row == 0
    assert game.current_col == 4

    qtbot.keyClick(game, Qt.Key.Key_Return)

    assert game.current_row == 1
    assert game.current_col == 0


def test_priorita_colori_tastiera(game):
    """Verifica che il verde non venga sovrascritto dal giallo o dal grigio."""
    btn = game.keyboard_buttons.get("A")
    assert btn is not None

    game._aggiorna_colore_tasto("A", "#b59f3b")
    assert "#b59f3b" in btn.styleSheet()

    game._aggiorna_colore_tasto("A", "#538d4e")
    assert "#538d4e" in btn.styleSheet()

    game._aggiorna_colore_tasto("A", "#b59f3b")
    assert "#538d4e" in btn.styleSheet()


def test_colorazione_griglia_con_manager(game):
    """Verifica che le celle prendano i colori giusti in base alla risposta del backend."""
    mock_manager = MagicMock()
    mock_manager.submit_guess.return_value = [
        "Corretto",
        "Presente",
        "Assente",
        "Assente",
        "Assente",
    ]
    mock_manager.is_game_over.return_value = False
    game.GameManager = mock_manager

    for char in "PARCO":
        game._ui_on_key_press(char)

    game._ui_on_enter()

    assert "#538d4e" in game.grid[0][0].styleSheet()
    assert "#b59f3b" in game.grid[0][1].styleSheet()
    assert "#3a3a3c" in game.grid[0][2].styleSheet()

    assert game.current_row == 1


def test_digitazione_oltre_limite_riga(game):
    """Verifica che scrivendo 6 lettere sulla stessa riga, l'ultima non sovrascriva la 5°."""
    for char in "HELLO":
        game._ui_on_key_press(char)

    assert game.current_col == 5
    assert game.grid[0][4].toPlainText() == "O"

    game._ui_on_key_press("X")

    assert game.current_col == 5
    assert game.grid[0][4].toPlainText() == "O"


def test_backspace_inizio_riga_sicuro(game):
    """Verifica che premere backspace colonna 0 non generi errori."""
    assert game.current_col == 0
    game._ui_on_backspace()
    assert game.current_col == 0


def test_gioco_finito_blocca_input(game, qtbot):
    """Verifica che a partita finita l'interfaccia non accetti più input."""
    game.gioco_finito = True

    game._ui_on_key_press("A")
    qtbot.keyClick(game, Qt.Key.Key_B)

    assert game.grid[0][0].toPlainText() == ""
    assert game.current_col == 0
