"""Modulo per la finestra di gioco di Wordle."""

import os
import sys
from typing import Any, List, Type

try:
    from PyQt6 import QtCore, QtWidgets, uic
    from PyQt6.QtGui import QKeyEvent

    HAS_QT = True
    BaseWindow: Type[Any] = QtWidgets.QMainWindow
except ImportError:
    HAS_QT = False
    BaseWindow = object


class GameWindow(BaseWindow):
    """Classe che gestisce la logica della griglia e della tastiera di gioco."""

    def __init__(self, nome_giocatore: str = "Giocatore"):
        """Inizializza la finestra, carica l'UI e prepara la griglia."""
        self.grid: List[List[Any]] = [[None for _ in range(5)] for _ in range(6)]
        self.nome_giocatore = nome_giocatore
        self.current_row = 0
        self.current_col = 0

        if not HAS_QT:
            return

        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "game_window.ui")

        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            print(f"Errore: Il file {ui_path} non esiste!")

        self._map_ui_grid()
        self._setup_keyboard()
        self.setup_keyboard_focus()
        self._refresh_ui_state()

        if hasattr(self, "pushButton"):
            self.pushButton.clicked.connect(self.close)

    def _map_ui_grid(self):
        """Mappa i QTextEdit basandosi sulla loro posizione nel QGridLayout."""
        grid_layout = self.findChild(QtWidgets.QGridLayout, "gridLayout")
        if not grid_layout:
            print("Errore: gridLayout assente")
            return

        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

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

    def _refresh_ui_state(self):
        """Aggiorna lo stato visivo."""
        for r in range(6):
            for c in range(5):
                widget = self.grid[r][c]

                if widget is None:
                    continue

                is_active = r == self.current_row and c == self.current_col

                if is_active:
                    widget.setStyleSheet("""
                        background-color: white; 
                        color: black; 
                        border: 3px solid #538d4e; 
                        font-weight: bold; font-size: 25px;
                    """)
                    widget.setFocus()
                else:
                    widget.setStyleSheet("""
                        background-color: white; 
                        color: black; 
                        border: 2px solid #d3d6da;
                        font-size: 25px;
                    """)

                widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def _setup_keyboard(self):
        """Crea la tastiera dinamica."""
        if not hasattr(self, "keyboard_container") or self.keyboard_container is None:
            return

        if self.keyboard_container.layout():
            layout = self.keyboard_container.layout()
        else:
            layout = QtWidgets.QVBoxLayout(self.keyboard_container)

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
                btn.setMinimumHeight(40)
                btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #538d4e; color: white; 
                        border-radius: 4px; font-weight: bold; 
                    }
                    QPushButton:hover { background-color: #565758; }
                """)

                if key == "INVIO":
                    btn.clicked.connect(self._ui_on_enter)
                elif key == "⌫":
                    btn.clicked.connect(self._ui_on_backspace)
                else:
                    btn.clicked.connect(lambda checked, k=key: self._ui_on_key_press(k))

                h_layout.addWidget(btn)
            layout.addLayout(h_layout)

    def _ui_on_key_press(self, char: str):
        if self.current_col < 5:
            widget = self.grid[self.current_row][self.current_col]
            if widget:
                widget.setText(char)
                widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                if self.current_col < 4:
                    self.current_col += 1
                    self._refresh_ui_state()

    def _ui_on_backspace(self):
        widget = self.grid[self.current_row][self.current_col]
        if widget and widget.toPlainText():
            widget.clear()
        elif self.current_col > 0:
            self.current_col -= 1
            if self.grid[self.current_row][self.current_col]:
                self.grid[self.current_row][self.current_col].clear()
        self._refresh_ui_state()

    def _ui_on_enter(self):
        if self.current_col == 4 and self.grid[self.current_row][4].toPlainText():
            if self.current_row < 5:
                self.current_row += 1
                self.current_col = 0
                self._refresh_ui_state()

    def setup_keyboard_focus(self):
        """Assicura che le celle non rubino il focus alla finestra."""
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    cell.setReadOnly(True)
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
    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())
