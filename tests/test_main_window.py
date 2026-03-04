"""Unit tests per l'interfaccia grafica principale."""

import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

@pytest.fixture(name="app")
def fixture_app():
    """Fixture per creare l'istanza QApplication necessaria per i widget."""

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

def test_main_window_initialization(app): # pylint: disable=redefined-outer-name, unused-argument
    """Verifica che la MainWindow si carichi senza errori e abbia i testi corretti."""
    window = MainWindow(nome_giocatore="TestPlayer")
    
    assert window is not None
    
    assert "TestPlayer" in window.lbl_welcome.text()
    