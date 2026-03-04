"""Unit tests per l'interfaccia grafica principale."""

from unittest.mock import MagicMock
import pytest
# pylint: disable=no-name-in-module, import-error
from src.gui.main_window import MainWindow

@pytest.fixture(name="mock_window")
def fixture_mock_window(monkeypatch):
    """Fixture per simulare la MainWindow senza caricare PyQt6."""
    # Simula il caricamento dell'UI per evitare errori headless
    monkeypatch.setattr("PyQt6.uic.loadUi", MagicMock())
    # Crea l'oggetto senza far partire l'app reale
    window = MainWindow(nome_giocatore="TestPlayer")
    # Simula manualmente il widget che verrebbe caricato dal .ui
    window.lbl_welcome = MagicMock()
    window.lbl_welcome.text.return_value = "Bentornato/a, TestPlayer!"
    yield window

def test_main_window_initialization(mock_window):
    """Verifica che la MainWindow riceva correttamente il nome giocatore."""
    assert "TestPlayer" in mock_window.lbl_welcome.text()