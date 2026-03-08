import os

import pytest

from src.gui.leaderboard_window import LeaderboardWindow

os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture
def app(qtbot):
    test_window = LeaderboardWindow()
    qtbot.addWidget(test_window)
    return test_window


def test_sorting_logic():
    dati = [
        {"utente": "B", "vittorie": 10, "media": 4.0},
        {"utente": "A", "vittorie": 10, "media": 3.0},
        {"utente": "C", "vittorie": 15, "media": 5.0},
    ]
    ordinati = sorted(dati, key=lambda x: (-x["vittorie"], x["media"]))

    assert ordinati[0]["utente"] == "C"
    assert ordinati[1]["utente"] == "A"
    assert ordinati[2]["utente"] == "B"


def test_leaderboard_columns(app):
    assert app.table_top3.columnCount() == 4
    assert app.table_user_pos.columnCount() == 3


def test_user_position_display(app):
    dati_test = [
        {"utente": "Giocatore1", "vittorie": 5, "media": 3.0},
        {"utente": "Io", "vittorie": 2, "media": 4.0},
    ]
    app.popola_classifica(dati_test, nome_utente_corrente="Io")

    assert app.table_user_pos.rowCount() == 1
    assert app.table_user_pos.item(0, 0).text() == "2"


def test_read_only_tables(app):
    from PyQt6.QtWidgets import QAbstractItemView

    assert app.table_top3.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers
    assert (
        app.table_user_pos.editTriggers()
        == QAbstractItemView.EditTrigger.NoEditTriggers
    )
