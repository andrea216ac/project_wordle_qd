"""Unit tests per la finestra della classifica di Wordle."""

# pylint: disable=no-name-in-module, import-outside-toplevel
import os
from typing import Any, cast
import pytest

from src.gui.leaderboard_window import LeaderboardWindow, HAS_QT

try:
    from PyQt6.QtWidgets import QAbstractItemView
    QAbstract = cast(Any, QAbstractItemView)
except ImportError:
    QAbstract = cast(Any, object)

os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(name="leaderboard_app")
def fixture_leaderboard_app(request):
    """Inizializza la finestra della classifica per i test UI."""
    if not HAS_QT:
        pytest.skip("Librerie Qt non disponibili su questo sistema.")

    try:
        qtbot_inst = request.getfixturevalue("qtbot")
    except (pytest.FixtureLookupError, ImportError, RuntimeError):
        pytest.skip("Plugin pytest-qt o librerie grafiche non inizializzate.")
        return None

    test_window = LeaderboardWindow()
    qtbot_inst.addWidget(test_window)
    return test_window


def test_sorting_logic():
    """Verifica che l'ordinamento (vittorie decrescenti, media crescente) funzioni."""
    dati = [
        {"utente": "B", "vittorie": 10, "media": 4.0},
        {"utente": "A", "vittorie": 10, "media": 3.0},
        {"utente": "C", "vittorie": 15, "media": 5.0},
    ]
    ordinati = sorted(dati, key=lambda x: (-x["vittorie"], x["media"]))

    assert ordinati[0]["utente"] == "C"
    assert ordinati[1]["utente"] == "A"
    assert ordinati[2]["utente"] == "B"


def test_leaderboard_columns(leaderboard_app):
    """Verifica il numero corretto di colonne nelle tabelle UI."""
    assert leaderboard_app.table_top3.columnCount() == 4
    assert leaderboard_app.table_user_pos.columnCount() == 3


def test_user_position_display(leaderboard_app):
    """Verifica che la posizione dell'utente corrente sia calcolata correttamente."""
    dati_test = [
        {"utente": "Giocatore1", "vittorie": 5, "media": 3.0},
        {"utente": "Io", "vittorie": 2, "media": 4.0},
    ]
    leaderboard_app.popola_classifica(dati_test, nome_utente_corrente="Io")

    assert leaderboard_app.table_user_pos.rowCount() == 1
    assert leaderboard_app.table_user_pos.item(0, 0).text() == "2"


def test_read_only_tables(leaderboard_app):
    """Assicura che le tabelle siano in modalità sola lettura."""
    no_edit = QAbstract.EditTrigger.NoEditTriggers
    assert leaderboard_app.table_top3.editTriggers() == no_edit
    assert leaderboard_app.table_user_pos.editTriggers() == no_edit
