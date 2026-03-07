"""Unit tests per la finestra principale."""

import os
import pytest
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt  # pylint: disable=no-name-in-module

from src.gui.main_window import MainWindow

os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(name="app_window")
def fixture_app_window(qtbot):
    """Inizializza la finestra per i test."""
    window = MainWindow(nome_giocatore="Tester")
    qtbot.addWidget(window)
    return window

def test_welcome_message(app_window):
    """Verifica il messaggio di benvenuto."""
    assert hasattr(app_window, "lbl_welcome")
    assert app_window.lbl_welcome.text() == "Bentornato/a, Tester!"

def test_exit_button_functional(app_window, qtbot):
    """Verifica il tasto exit."""
    qtbot.mouseClick(app_window.btn_exit, Qt.MouseButton.LeftButton)
    assert not app_window.isVisible()

def test_ui_structure(app_window):
    """Verifica il caricamento dei widget."""
    # pylint: disable=c-extension-no-member
    labels = app_window.findChildren(QtWidgets.QLabel)
    buttons = app_window.findChildren(QtWidgets.QPushButton)
    
    assert len(labels) > 0
    assert len(buttons) > 0
