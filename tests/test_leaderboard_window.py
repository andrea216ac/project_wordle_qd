"""Unit tests per la finestra della classifica di Wordle."""

# pylint: disable=no-name-in-module, import-outside-toplevel
import os
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from src.gui.leaderboard_window import HAS_QT, LeaderboardWindow

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
    assert leaderboard_app.table_user_pos.item(0, 0).text() == "2°"


def test_read_only_tables(leaderboard_app):
    """Assicura che le tabelle siano in modalità sola lettura."""
    no_edit = QAbstract.EditTrigger.NoEditTriggers
    assert leaderboard_app.table_top3.editTriggers() == no_edit
    assert leaderboard_app.table_user_pos.editTriggers() == no_edit


def test_torna_indietro_logic(leaderboard_app):
    """Verifica che il metodo torna_indietro non crashi."""
    leaderboard_app.torna_indietro()
    assert leaderboard_app.main_window is not None


def test_torna_indietro_calls_show_on_main_window(leaderboard_app):
    """Verifica che premendo 'indietro' venga mostrata la MainWindow precedente."""
    mock_main = MagicMock()
    leaderboard_app.main_window = mock_main

    leaderboard_app.torna_indietro()

    mock_main.show.assert_called_once()


def test_popola_classifica_empty(leaderboard_app):
    """Verifica che il popolamento funzioni anche con dati vuoti."""
    leaderboard_app.popola_classifica([], nome_utente_corrente="Nessuno")
    assert leaderboard_app.table_top3.rowCount() == 0
    assert leaderboard_app.table_user_pos.rowCount() == 0


def test_user_not_in_leaderboard(leaderboard_app):
    """Verifica il comportamento se l'utente corrente non è in classifica."""
    dati_test = [{"utente": "Player1", "vittorie": 1, "media": 5.0}]
    leaderboard_app.popola_classifica(dati_test, nome_utente_corrente="Sconosciuto")
    assert leaderboard_app.table_user_pos.rowCount() == 0


def test_aggiorna_classifica_with_mock_manager(qtbot):
    """Verifica che la finestra scarichi e mostri i dati dal GameManager all'avvio."""
    mock_manager = MagicMock()
    mock_manager.get_leaderboard.return_value = [
        {"utente": "Mario", "vittorie": 10, "media": 3.5}
    ]
    mock_manager.get_current_user.return_value = "Mario"

    window = LeaderboardWindow(game_manager=mock_manager)
    qtbot.addWidget(window)

    assert window.table_top3.rowCount() == 1
    assert window.table_top3.item(0, 1).text() == "Mario"
