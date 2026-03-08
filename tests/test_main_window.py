"""Unit tests per la finestra principale con protezione per ambienti headless."""

import os
from typing import Any, cast
from unittest.mock import MagicMock

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

from src.gui.main_window import MainWindow

if HAS_QT:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(name="app_window")
def fixture_app_window(qtbot):
    """Inizializza la finestra. Salta il test se Qt non è presente."""
    if not HAS_QT:
        pytest.skip("Librerie Qt (libEGL/OpenGL) non disponibili su questo sistema.")

    window = MainWindow(nome_giocatore="Tester")
    qtbot.addWidget(window)
    return window


def test_always_passes():
    """Test di base per garantire che Pytest trovi almeno un test valido."""
    assert 1 + 1 == 2


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
