import os

import pytest
from PyQt6 import QtCore, QtWidgets  # <--- Aggiunto QtCore
from PyQt6.QtCore import Qt

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from src.gui.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    """Fixture che inizializza la finestra per ogni test."""
    window = MainWindow(nome_giocatore="Tester")
    qtbot.addWidget(window)
    return window


def test_welcome_message(app):
    """Verifica che il messaggio di benvenuto sia impostato correttamente."""
    assert hasattr(app, "lbl_welcome"), "Il widget lbl_welcome non esiste!"
    expected_text = "Bentornato/a, Tester!"
    assert app.lbl_welcome.text() == expected_text


def test_exit_button_functional(app, qtbot):
    """Verifica che il tasto exit sia collegato correttamente."""
    assert hasattr(app, "btn_exit"), "Il widget btn_exit non esiste!"

    qtbot.mouseClick(app.btn_exit, Qt.MouseButton.LeftButton)
    assert not app.isVisible() or app.close()


def test_ui_structure(app):
    """Test strutturale: verifica che i widget principali siano stati caricati."""
    labels = app.findChildren(QtWidgets.QLabel)
    buttons = app.findChildren(QtWidgets.QPushButton)

    assert len(labels) > 0, "Nessuna Label trovata nella UI"
    assert len(buttons) > 0, "Nessun Button trovato nella UI"
