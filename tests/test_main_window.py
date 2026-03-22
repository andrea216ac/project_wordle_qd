"""Unit tests per la finestra principale con protezione per ambienti headless."""

import os
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

try:
    from PyQt6 import QtCore as real_core
    from PyQt6 import QtWidgets as real_widgets
    from PyQt6.QtCore import Qt as real_qt  # pylint: disable=no-name-in-module

    QtWidgets = cast(Any, real_widgets)  # pylint: disable=invalid-name
    QtCore = cast(Any, real_core)  # pylint: disable=invalid-name
    Qt = cast(Any, real_qt)  # pylint: disable=invalid-name
    HAS_QT = True
except ImportError:
    QtWidgets = cast(Any, MagicMock())  # pylint: disable=invalid-name
    QtCore = cast(Any, MagicMock())  # pylint: disable=invalid-name
    Qt = cast(Any, MagicMock())  # pylint: disable=invalid-name
    HAS_QT = False

from src.core.game_manager import GameManager
from src.gui.main_window import MainWindow

if HAS_QT:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(name="app_window")
def fixture_app_window(request):
    """Inizializza la finestra della main window per i test UI."""
    if not HAS_QT:
        pytest.skip("Librerie Qt non disponibili")

    if "qtbot" not in request.fixturenames:
        pytest.skip("Plugin pytest-qt non installato o non configurato")
        return None

    qtbot_inst = request.getfixturevalue("qtbot")

    mock_manager = MagicMock(spec=GameManager)

    window = MainWindow(nome_giocatore="Tester", game_manager=mock_manager)
    qtbot_inst.addWidget(window)
    return window


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_welcome_message(app_window):
    """Verifica che il messaggio di benvenuto sia impostato correttamente."""
    assert hasattr(app_window, "lbl_welcome")
    assert app_window.lbl_welcome.text() == "Bentornato/a, Tester!"


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_exit_button_functional(app_window, qtbot):
    """Verifica che il tasto exit chiuda la finestra."""
    # pylint: disable=no-member
    qtbot.mouseClick(app_window.btn_exit, Qt.MouseButton.LeftButton)
    assert not app_window.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_leaderboard_button_functional(app_window, qtbot):
    """Verifica che il tasto classifica apra la relativa finestra."""
    # pylint: disable=no-member
    qtbot.mouseClick(app_window.btn_leaderboard, Qt.MouseButton.LeftButton)
    assert not app_window.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_ui_structure(app_window):
    """Verifica il caricamento dinamico dei widget dal file .ui."""
    # pylint: disable=c-extension-no-member
    labels = app_window.findChildren(QtWidgets.QLabel)
    buttons = app_window.findChildren(QtWidgets.QPushButton)
    assert len(labels) > 0
    assert len(buttons) > 0


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_leaderboard_reference_passing(app_window, qtbot):
    """Verifica che la MainWindow passi se stessa alla LeaderboardWindow."""
    qtbot.mouseClick(app_window.btn_leaderboard, Qt.MouseButton.LeftButton)

    assert app_window.leaderboard_window is not None
    assert app_window.leaderboard_window.main_window == app_window


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_new_game_button_functional(app_window, qtbot):
    """Verifica che il tasto Nuova Partita apra la GameWindow e chiuda la MainWindow."""
    # pylint: disable=no-member

    assert hasattr(app_window, "btn_play")

    qtbot.mouseClick(app_window.btn_play, Qt.MouseButton.LeftButton)

    assert not app_window.isVisible()

    assert app_window.game_window is not None

    assert app_window.game_window.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_training_button_functional(app_window, qtbot):
    """Verifica che il tasto Allenamento apra la GameWindow in modalità training."""
    assert hasattr(
        app_window, "btn_training"
    ), "Il bottone btn_training non è presente nel file .ui"

    # pylint: disable=no-member
    qtbot.mouseClick(app_window.btn_training, Qt.MouseButton.LeftButton)

    assert not app_window.isVisible()

    assert app_window.game_window is not None

    assert app_window.game_window.modalita == "training"
    assert app_window.game_window.isVisible()


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI: librerie grafiche mancanti")
def test_different_modes_setup(app_window, qtbot):
    """Verifica che i due bottoni (Play e Training) lancino modalità diverse."""
    qtbot.mouseClick(app_window.btn_play, Qt.MouseButton.LeftButton)
    assert app_window.game_window.modalita == "classic"

    app_window.show()

    qtbot.mouseClick(app_window.btn_training, Qt.MouseButton.LeftButton)
    assert app_window.game_window.modalita == "training"


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_play_button_disabled_if_already_played(qtbot):
    """Verifica che btn_play sia disabilitato se l'utente ha già giocato oggi."""
    mock_manager = MagicMock()
    mock_manager.has_played_classic_today.return_value = True

    window = MainWindow(nome_giocatore="Tester", game_manager=mock_manager)
    qtbot.addWidget(window)

    assert not window.btn_play.isEnabled()
    assert window.btn_play.text() == "Già giocato"


@pytest.mark.skipif(not HAS_QT, reason="Salto test GUI")
def test_avvia_gioco_runtime_error_handling(app_window, qtbot):
    """Verifica che un RuntimeError generi un avviso e disabiliti il pulsante classic."""

    with patch(
        "src.gui.game_window.GameWindow", side_effect=RuntimeError("Limite raggiunto")
    ):
        with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:

            qtbot.mouseClick(app_window.btn_play, Qt.MouseButton.LeftButton)

            mock_warning.assert_called_once()

            assert not app_window.btn_play.isEnabled()
            assert app_window.btn_play.text() == "Già giocato"
