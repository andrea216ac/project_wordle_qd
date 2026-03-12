import os
import sys
from typing import List

from PyQt6 import QtCore, QtWidgets, uic


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, nome_giocatore: str = "Giocatore"):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "game_window.ui")
        uic.loadUi(ui_path, self)

        self.nome_giocatore = nome_giocatore
        self.current_row = 0
        self.current_col = 0

        self.grid: List[List[QtWidgets.QTextEdit]] = [
            [None for _ in range(5)] for _ in range(6)
        ]

        self._map_ui_grid()
        self._setup_keyboard()
        self._refresh_ui_state()

        if hasattr(self, "pushButton"):
            self.pushButton.clicked.connect(self.close)

    def _map_ui_grid(self):
        """Mappa i QTextEdit del file UI nella nostra matrice interna."""
        grid_layout = self.findChild(QtWidgets.QGridLayout, "gridLayout")
        for i in range(grid_layout.count()):
            widget = grid_layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QTextEdit):
                idx = grid_layout.indexOf(widget)
                row, col, _, _ = grid_layout.getItemPosition(idx)
                self.grid[row][col] = widget
                widget.setReadOnly(True)
                widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def _setup_keyboard(self):
        """Crea la tastiera QWERTY nel container."""
        if not hasattr(self, "keyboard_container"):
            return

        layout = QtWidgets.QVBoxLayout(self.keyboard_container)
        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["INVIO", "Z", "X", "C", "V", "B", "N", "M", "⌫"],
        ]

        for row_keys in rows:
            h_layout = QtWidgets.QHBoxLayout()
            for key in row_keys:
                btn = QtWidgets.QPushButton(key)
                btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
                btn.setMinimumHeight(40)
                if key == "INVIO":
                    btn.clicked.connect(self._ui_on_enter)
                elif key == "⌫":
                    btn.clicked.connect(self._ui_on_backspace)
                else:
                    btn.clicked.connect(lambda checked, k=key: self._ui_on_key_press(k))

                h_layout.addWidget(btn)
            layout.addLayout(h_layout)

    def _refresh_ui_state(self):
        """Aggiorna i colori e l'abilitazione delle celle in base alla posizione."""
        for r in range(6):
            for c in range(5):
                is_active = r == self.current_row and c == self.current_col
                self.grid[r][c].setEnabled(is_active)
                if is_active:
                    self.grid[r][c].setStyleSheet(
                        "border: 2px solid #538d4e; background: #3a3a3c; color: white;"
                    )
                    self.grid[r][c].setFocus()
                else:
                    self.grid[r][c].setStyleSheet(
                        "border: 1px solid #3a3a3c; background: #121213; color: gray;"
                    )

    def _ui_on_key_press(self, char: str):
        if self.current_col < 5:
            self.grid[self.current_row][self.current_col].setText(char)
            if self.current_col < 4:
                self.current_col += 1
                self._refresh_ui_state()

    def _ui_on_backspace(self):
        if self.current_col > 0:
            if not self.grid[self.current_row][self.current_col].toPlainText():
                self.current_col -= 1
            self.grid[self.current_row][self.current_col].clear()
            self._refresh_ui_state()

    def _ui_on_enter(self):
        """Qui è dove la UI chiama la logica del tuo collaboratore."""
        parola_inserita = "".join(
            [self.grid[self.current_row][c].toPlainText() for c in range(5)]
        )

        if len(parola_inserita) < 5:
            print("Parola troppo corta!")
            return

        if self.current_row < 5:
            self.current_row += 1
            self.current_col = 0
            self._refresh_ui_state()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())
