"""Game modes for Wordle: ClassicMode and TrainingMode."""

import datetime
import logging
import random
from typing import Optional

from word_provider import WordProvider
from game import Game


logger = logging.getLogger(__name__)


class ClassicMode:
    """
    ClassicMode: one word per day, score increases when the word is guessed.
    """