"""Modulo per la finestra della classifica dell'applicazione Wordle."""

# pylint: disable=duplicate-code
import os
import sys
from typing import Any, Type

# pylint: disable=no-name-in-module, no-member, c-extension-no-member
try:
    from PyQt6 import QtCore,QtWidgets, uic
    from PyQt6.QtWidgets import QHeaderView, QTableWidgetItem

    HAS_QT = True
    BaseDialog: Type[Any] = QtWidgets.QDialog
except ImportError:
    HAS_QT = False
    BaseDialog = object


class LeaderboardWindow(BaseDialog):
    """Classe che gestisce la visualizzazione della classifica utenti."""

    def __init__(self, main_window=None, game_manager=None):
        """Inizializza la finestra e carica i dati della classifica."""
        super().__init__()

        self.main_window = main_window
        self.game_manager = game_manager

        ui_path = os.path.join(os.path.dirname(__file__), "leaderboard_window.ui")

        if not os.path.exists(ui_path):
            print(f"Errore: Il file {ui_path} non esiste!")
            return

        uic.loadUi(ui_path, self)

        self.table_top3.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_user_pos.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Configurazione bottone indietro
        btn_back = getattr(self, "btn_back", None)
        if btn_back:
            btn_back.clicked.connect(self.torna_indietro)

        # Controllo esistenza tabelle nell'UI
        if hasattr(self, "table_top3") and hasattr(self, "table_user_pos"):
            self.setup_leaderboard_graphics()
            self.aggiorna_classifica() # Carica i dati reali
            self.adatta_font_dinamico()
        else:
            print("ERRORE: Tabelle non trovate nel file .ui. Verifica gli objectName.")

    def setup_leaderboard_graphics(self):
        """Configura le intestazioni e il comportamento delle tabelle."""
        # Tabella Top 3
        self.table_top3.setColumnCount(4)
        self.table_top3.setHorizontalHeaderLabels(["Pos.", "Utente", "Vittorie", "Media Tentativi"])
        self.table_top3.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_top3.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Tabella Posizione Utente
        self.table_user_pos.setColumnCount(3)
        self.table_user_pos.setHorizontalHeaderLabels(["Posizione", "Vittorie", "Media Tentativi"])
        self.table_user_pos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_user_pos.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

    def aggiorna_classifica(self):
        """Recupera i dati aggiornati tramite GameManager e popola la UI."""
        dati = []
        nome_utente = "Ospite"
        
        if self.game_manager:
            # 1. Recupera la lista dei punteggi
            dati = self.game_manager.get_leaderboard()
            # 2. Recupera il nome dell'utente loggato (per evidenziarlo in classifica)
            nome_utente = self.game_manager.get_current_user() or "Ospite"
        else:
            print("Attenzione: GameManager non passato alla LeaderboardWindow.")

        # Passiamo ENTRAMBI i parametri richiesti
        self.popola_classifica(dati, nome_utente)

    def popola_classifica(self, dati, nome_utente_corrente):
        """Popola le tabelle e forza la ricerca dell'utente corrente."""
        
        # 1. Popola Top 3
        self.table_top3.setRowCount(0) # Reset totale
        self.table_top3.setRowCount(min(3, len(dati)))
        for i in range(min(3, len(dati))):
            g = dati[i]
            self._inserisci_riga_centrata(self.table_top3, i, [
                str(i + 1), g["utente"], str(g["vittorie"]), f"{g['media']:.2f}"
            ])

        # 2. Logica per la posizione dell'utente corrente
        self.table_user_pos.setRowCount(1)
        self.table_user_pos.setRowHeight(0, 60)
        
        dati_utente = None
        pos_utente = -1
        
        # Normalizzazione del nome (rimuove spazi e rende minuscolo)
        target = str(nome_utente_corrente or "").strip().lower()
        
        # DEBUG (Opzionale: controlla la console se non lo trovi)
        # print(f"DEBUG: Cerco '{target}' tra {len(dati)} utenti")

        if target and target != "ospite":
            for index, g in enumerate(dati):
                # Confronto ultra-sicuro
                nome_in_lista = str(g.get("utente", "")).strip().lower()
                if nome_in_lista == target:
                    pos_utente = index + 1
                    dati_utente = g
                    break

        if dati_utente:
            self._inserisci_riga_centrata(self.table_user_pos, 0, [
                f"{pos_utente}°", 
                str(dati_utente["vittorie"]), 
                f"{dati_utente['media']:.2f}"
            ])
        else:
            # Se non trovato o se è "Ospite", mostra valori di default
            self._inserisci_riga_centrata(self.table_user_pos, 0, ["-", "0", "0.00"])

    def _inserisci_riga_centrata(self, tabella, riga, valori):
        """Utility per inserire una riga con testo centrato."""
        for col, valore in enumerate(valori):
            item = QTableWidgetItem(valore)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            tabella.setItem(riga, col, item)
            
    def showEvent(self, event):
        """Metodo standard di Qt chiamato ogni volta che la finestra viene mostrata."""
        super().showEvent(event)
        self.aggiorna_classifica() # Riesegue la query al DB ogni volta che la finestra si apre

    def torna_indietro(self):
        """Metodo per tornare alla main window evitando crash se il manager è None."""
        from src.gui.main_window import MainWindow

        # Recuperiamo il nome in sicurezza
        username = "Ospite"
        if self.game_manager is not None:
            username = self.game_manager.get_current_user() or "Ospite"

        if self.main_window is None:
            # Passiamo i dati necessari alla MainWindow
            self.main_window = MainWindow(
                nome_giocatore=username,
                game_manager=self.game_manager
            )

        self.main_window.show()
        self.close()

    def resizeEvent(self, event):
        """Ricalcola la dimensione dei font quando la finestra cambia dimensione."""
        super().resizeEvent(event)
        self.adatta_font_dinamico()

    def adatta_font_dinamico(self):
        """Calcola una dimensione del font proporzionale alla larghezza della finestra."""
        w = self.width()
        # Calcolo dimensioni proporzionali
        size_titolo = max(22, int(w / 30))
        size_tabella = max(16, int(w / 40))
        size_header = max(14, int(w / 50))

        stile_globale = f"""
            QDialog {{ background-color: #121213; }}
            QLabel {{ 
                color: #ffffff; 
                font-weight: bold; 
                font-size: {size_titolo}px; 
                margin-bottom: 10px;
            }}
            
            QTableWidget {{ 
                background-color: #121213; 
                color: white; 
                gridline-color: #3a3a3c; 
                border: 1px solid #3a3a3c; 
                font-size: {size_tabella}px;
                outline: 0; 
            }}
            QTableWidget::item {{ 
                padding: 10px;
            }}
            QHeaderView::section {{ 
                background-color: #538d4e; 
                color: white; 
                font-weight: bold; 
                font-size: {size_header}px; 
                border: 1px solid #3a3a3c;
                text-align: center;
            }}
            QPushButton#btn_back {{ 
                background-color: #538d4e; color: white; border-radius: 4px; 
                padding: 10px; font-size: {max(16, size_header)}px; 
            }}
            QPushButton#btn_back:hover {{ background-color: #6aaa64; }}
        """
        self.setStyleSheet(stile_globale)

        # Centriamo il testo di TUTTE le celle e delle intestazioni
        for table in [self.table_top3, self.table_user_pos]:
            # 1. Centra le intestazioni delle colonne
            table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            
            # 2. Centra il contenuto di ogni cella
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def _crea_item_centrato(self, testo):
        """Utility per creare un item già centrato."""
        item = QTableWidgetItem(str(testo))
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        return item

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LeaderboardWindow()
    window.show()
    sys.exit(app.exec())
