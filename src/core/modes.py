"""Metodi di Gioco: ClassicMode and TrainingMode."""

import datetime
import logging
import random
from typing import Optional

from word_provider import WordProvider
from game import Game


logger = logging.getLogger(__name__)


class ClassicMode:
    """
    ClassicMode: una parola al giorno
    """