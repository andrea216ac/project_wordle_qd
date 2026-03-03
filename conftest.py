"""
Configurazione per pytest e gestione dei path.
"""

import sys
import os

# Aggiunge la cartella 'src' al percorso di ricerca di Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
