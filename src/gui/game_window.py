# pylint: disable=no-member, invalid-name, c-extension-no-member
"""Modulo per la finestra di gioco di Wordle."""

import os
import sys
from typing import Any, List, Optional, Type

from src.core.game_manager import GameManager

try:
    from PyQt6 import QtCore, QtWidgets, uic
    from PyQt6.QtGui import QKeyEvent

    HAS_QT = True
    BaseWindow: Type[Any] = QtWidgets.QMainWindow
except ImportError:
    HAS_QT = False
    BaseWindow = object


# pylint: disable=too-many-instance-attributes
class GameWindow(BaseWindow):
    """Classe che gestisce la logica della griglia e della tastiera di gioco."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        main_window=None,
        nome_giocatore: str = "Giocatore",
        *,
        game_manager: Optional[GameManager] = None,
        modalita: str = "classic",
        lingua: str = "it",
    ):
        """Inizializza la finestra, carica l'UI e prepara la griglia."""
        self.grid: List[List[Any]] = [[None for _ in range(5)] for _ in range(6)]
        self.keyboard_buttons: dict[str, QtWidgets.QPushButton] = {}

        self.nome_giocatore = nome_giocatore
        self.current_row = 0
        self.current_col = 0

        self.game_manager = game_manager
        self.gioco_finito = False

        if not HAS_QT:
            return

        super().__init__()
        self.main_window = main_window
        ui_path = os.path.join(os.path.dirname(__file__), "game_window.ui")

        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            print(f"Errore: Il file {ui_path} non esiste!")

        self._map_ui_grid()
        self._setup_keyboard()
        self.setup_keyboard_focus()

        btn_back = getattr(self, "btn_back", None)
        if btn_back:
            btn_back.clicked.connect(self.torna_indietro)

        if self.game_manager:
            self.game_manager.start_game(
                mode=modalita, language=lingua, user=nome_giocatore
            )
            self._ripristina_interfaccia()

        self._refresh_ui_state()

    def _ripristina_interfaccia(self):
        """Carica visivamente i tentativi passati sulla griglia."""
        if not self.game_manager or not self.game_manager.current_mode:
            return

        game = self.game_manager.current_mode.current_game
        if not game or not hasattr(game, "guesses") or not game.guesses:
            return

        target = game.target_word.upper()

        for i, guess in enumerate(game.guesses):
            guess = guess.upper()
            risultati = self._calcola_colori(guess, target)
            self._colora_riga(i, guess, risultati)
            self.current_row += 1

        if game.is_over:
            self.gioco_finito = True

    def _calcola_colori(self, guess: str, target: str) -> List[str]:
        """Calcola Verde/Giallo/Grigio senza alterare il punteggio interno."""
        res = ["Assente"] * 5
        t_chars = list(target)
        g_chars = list(guess)
        for i in range(5):
            if g_chars[i] == t_chars[i]:
                res[i] = "Corretto"
                t_chars[i] = None
        for i in range(5):
            if res[i] != "Corretto" and g_chars[i] in t_chars:
                res[i] = "Presente"
                t_chars[t_chars.index(g_chars[i])] = None
        return res

    def _colora_riga(self, riga: int, parola: str, risultati: List[str]):
        """Applica i CSS alla riga specifica."""
        color_map = {"Corretto": "#538d4e", "Presente": "#b59f3b", "Assente": "#3a3a3c"}
        for i, esito in enumerate(risultati):
            widget = self.grid[riga][i]
            colore = color_map.get(esito, "#3a3a3c")
            widget.setText(parola[i])
            widget.setStyleSheet(f"""
                background-color: {colore}; color: white;
                border: 2px solid {colore}; font-weight: bold; font-size: 25px;
            """)
            self._aggiorna_colore_tasto(parola[i], colore)

    def torna_indietro(self):
        """Metodo per tornare alla main window."""
        # pylint: disable=import-outside-toplevel, cyclic-import
        from src.gui.main_window import MainWindow

        if self.main_window is None:
            self.main_window = MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        self.close()

    def _map_ui_grid(self):
        """Mappa i QTextEdit basandosi sulla loro posizione nel QGridLayout."""
        grid_layout = self.findChild(QtWidgets.QGridLayout, "gridLayout")
        if not grid_layout:
            return

        grid_layout.setSpacing(5)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

        for i in range(grid_layout.count()):
            item = grid_layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, QtWidgets.QTextEdit):
                row, col, _, _ = grid_layout.getItemPosition(i)
                if row < 6 and col < 5:
                    self.grid[row][col] = widget
                    widget.setFixedSize(60, 60)
                    widget.setReadOnly(True)
                    widget.setVerticalScrollBarPolicy(
                        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                    )
                    widget.setHorizontalScrollBarPolicy(
                        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                    )
                    widget.setTextInteractionFlags(
                        QtCore.Qt.TextInteractionFlag.NoTextInteraction
                    )
                    widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def _refresh_ui_state(self):
        """Aggiorna lo stato visivo SOLO per la riga in corso."""
        if self.gioco_finito or self.current_row > 5:
            return

        for c in range(5):
            widget = self.grid[self.current_row][c]
            if widget is None:
                continue

            is_active = c == self.current_col

            if is_active:
                widget.setStyleSheet("""
                    background-color: #3a3a3c; 
                    color: white; 
                    border: 3px solid #538d4e; 
                    font-weight: bold; font-size: 25px;
                """)
            else:
                has_text = bool(widget.toPlainText())
                border_color = "#565758" if has_text else "#3a3a3c"
                widget.setStyleSheet(f"""
                    background-color: #121213; 
                    color: white; 
                    border: 2px solid {border_color};
                    font-weight: bold; font-size: 25px;
                """)

    def _setup_keyboard(self):
        """Crea la tastiera dinamica e salva i riferimenti ai bottoni."""
        if not hasattr(self, "keyboard_container") or self.keyboard_container is None:
            return

        layout = self.keyboard_container.layout() or QtWidgets.QVBoxLayout(
            self.keyboard_container
        )
        layout.setSpacing(5)

        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["INVIO", "Z", "X", "C", "V", "B", "N", "M", "⌫"],
        ]

        for row_keys in rows:
            h_layout = QtWidgets.QHBoxLayout()
            for key in row_keys:
                btn = QtWidgets.QPushButton(key)
                btn.setMinimumHeight(50)
                if len(key) > 1:
                    btn.setFixedWidth(25)
                else:
                    btn.setFixedWidth(25)
                btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

                btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #818384; color: white; 
                        border-radius: 4px; font-weight: bold; font-size: 16px;
                    }
                    QPushButton:hover { background-color: #565758; }
                """)

                if key == "INVIO":
                    btn.clicked.connect(self._ui_on_enter)
                elif key == "⌫":
                    btn.clicked.connect(self._ui_on_backspace)
                else:
                    self.keyboard_buttons[key] = btn
                    btn.clicked.connect(lambda checked, k=key: self._ui_on_key_press(k))

                h_layout.addWidget(btn)
            layout.addLayout(h_layout)

    def _ui_on_key_press(self, char: str):
        if self.gioco_finito:
            return

        if self.current_col < 5:
            widget = self.grid[self.current_row][self.current_col]
            if widget:
                widget.setText(char)
                widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                if self.current_col < 4:
                    self.current_col += 1
                elif self.current_col == 4 and not widget.toPlainText():
                    pass
                else:
                    self.current_col = 5

                self._refresh_ui_state()

    def _ui_on_backspace(self):
        if self.gioco_finito:
            return

        if self.current_col == 5:
            self.current_col = 4

        widget = self.grid[self.current_row][self.current_col]

        if widget and widget.toPlainText():
            widget.clear()
        elif self.current_col > 0:
            self.current_col -= 1
            self.grid[self.current_row][self.current_col].clear()

        self._refresh_ui_state()

    def _ui_on_enter(self):
        """Valida la parola inserita, colora le celle e avanza di riga."""
        if self.gioco_finito or self.current_row > 5:
            return

        if self.current_col == 5 or (
            self.current_col == 4 and self.grid[self.current_row][4].toPlainText()
        ):
            tentativo = "".join(
                [self.grid[self.current_row][c].toPlainText() for c in range(5)]
            )
            self._controlla_parola(tentativo)

    def _controlla_parola(self, tentativo: str):
        """Usa il GameManager per validare la parola e colora l'interfaccia."""
        if not self.game_manager:
            print("Errore: GameManager non collegato!")
            return

        risultati = self.game_manager.submit_guess(tentativo)

        if risultati is None:
            # Mostra un messaggio all'utente o semplicemente ignora l'invio
            QtWidgets.QMessageBox.warning(
                self, "Parola non valida", "La parola non è presente nel dizionario."
            )
            return

        color_map = {"Corretto": "#538d4e", "Presente": "#b59f3b", "Assente": "#3a3a3c"}

        for i, esito in enumerate(risultati):
            widget = self.grid[self.current_row][i]
            colore = color_map.get(esito, "#3a3a3c")
            lettera = tentativo[i]

            widget.setStyleSheet(f"""
                background-color: {colore};
                color: white; border: 2px solid {colore};
                font-weight: bold; font-size: 25px;
            """)

            btn = self.keyboard_buttons.get(lettera)
            if btn:
                old_style = btn.styleSheet()
                if "#538d4e" not in old_style:
                    if colore == "#538d4e" or (
                        colore == "#b59f3b" and "#b59f3b" not in old_style
                    ):
                        btn.setStyleSheet(
                            f"""QPushButton {{ background-color: {colore}; color: white;
                            border-radius: 4px; font-weight: bold; font-size: 16px;}}"""
                        )
                    elif colore == "#3a3a3c" and "#b59f3b" not in old_style:
                        btn.setStyleSheet(
                            "QPushButton {{ background-color: #3a3a3c; color: white;"
                            "border-radius: 4px;font-weight:bold;font-size:16px;}}"
                        )

        if self.game_manager.is_game_over():
            self.gioco_finito = True
            vittoria = all(esito == "Corretto" for esito in risultati)

            if vittoria:
                QtWidgets.QMessageBox.information(
                    self,
                    "Complimenti!",
                    f"Hai indovinato! Tentativi: {self.game_manager.get_attempts()}",
                )
            else:
                parola_corretta = self.game_manager.get_target_word()
                QtWidgets.QMessageBox.critical(
                    self,
                    "Partita finita",
                    f"Peccato, tentativi esauriti!\nLa parola era: {parola_corretta}",
                )
        else:
            self.current_row += 1
            self.current_col = 0
            self._refresh_ui_state()

    def _aggiorna_colore_tasto(self, lettera, nuovo_colore):
        """Aggiorna il colore del tasto solo se il nuovo colore è 'più importante'."""
        btn = self.keyboard_buttons.get(lettera)
        if not btn:
            return

        stile_attuale = btn.styleSheet()
        verde = "#538d4e"
        giallo = "#b59f3b"

        if verde in stile_attuale:
            return

        if giallo in stile_attuale and nuovo_colore != verde:
            return

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {nuovo_colore}; color: white;
                border-radius: 4px; font-weight: bold; font-size: 16px;
            }}
        """)

    def setup_keyboard_focus(self):
        """Assicura che le celle non rubino il focus alla finestra."""
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    cell.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def keyPressEvent(self, event: QKeyEvent):
        """Gestisce l'input dalla tastiera fisica del PC."""
        key = event.key()

        if QtCore.Qt.Key.Key_A <= key <= QtCore.Qt.Key.Key_Z:
            lettera = event.text().upper()
            self._ui_on_key_press(lettera)
        elif key == QtCore.Qt.Key.Key_Backspace:
            self._ui_on_backspace()
        elif key in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            self._ui_on_enter()
        elif key == QtCore.Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    if HAS_QT:
        app = QtWidgets.QApplication(sys.argv)
        window = GameWindow()
        window.show()
        sys.exit(app.exec())
