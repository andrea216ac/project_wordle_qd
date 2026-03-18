"""Game manager coordina le sessioni di gioco."""

import logging
from typing import List, Optional

from src.core.game import Game
from src.core.modes import ClassicMode, ModeError, TrainingMode
from src.core.word_provider import WordProvider
from src.database.game_repository import GameRepository

logger = logging.getLogger(__name__)


class GameManager:
    """Gestisce la logica dei giochi e delle modalità."""

    def __init__(
        self,
        word_provider: WordProvider,
        score_repository: Optional[GameRepository] = None,
    ) -> None:
        self.word_provider: WordProvider = word_provider
        self.score_repository = score_repository

        self.current_mode: Optional[ClassicMode | TrainingMode] = None
        self.language: Optional[str] = None
        self.current_user: Optional[str] = None

    def start_game(
        self,
        mode: str,
        language: str,
        user: Optional[str] = None,
    ) -> None:
        """
        Inizia un nuovo gioco nella modalità scelta


        Args:
            mode: "classic" or "training".
            language: lingua (e.g., "it", "en").
            user: Utente corrente.

        Raises:
            ModeError: Modalità non valida o il gioco non può iniziare.
            RuntimeError: Se l'utente ha già giocato oggi.
        """
        self.language = language
        self.current_user = user

        if mode == "classic":
            if self.score_repository and user:
                if self.score_repository.has_played_today(user):
                    logger.warning(
                        "User %s already played today's classic game",
                        user,
                    )
                    raise RuntimeError("Classic mode already played today")

            self.current_mode = ClassicMode(self.word_provider)

        elif mode == "training":
            self.current_mode = TrainingMode(self.word_provider)

        else:
            logger.error("Invalid mode requested: %s", mode)
            raise ModeError(f"Invalid mode: {mode}")

        try:
            self.current_mode.start_game(language)
            logger.info(
                "Game started | user=%s mode=%s language=%s",
                self.current_user,
                mode,
                language,
            )
        except ModeError as exc:
            logger.error("Failed to start game: %s", exc)
            raise

    def submit_guess(self, guess: str) -> List[str]:
        """
        Invia un tentativo alla partita.

        Args:
            guess: Parola inserita dal giocatore.

        Returns:
            Lista risultati lettere.

        Raises:
            RuntimeError: Se non esiste una partita attiva.
        """
        if self.current_mode is None:
            logger.error("Attempted guess without active game.")
            raise RuntimeError("No active game")
        
        # VALIDAZIONE PAROLA
        if not self.word_provider.is_valid_word(guess, self.language):
            logger.warning("Invalid word attempted: %s", guess)
            raise ValueError("Questa parola non esiste")

        result: List[str] = self.current_mode.submit_guess(guess)

        logger.info(
            "Guess submitted | user=%s guess=%s result=%s",
            self.current_user,
            guess,
            result,
        )
        game: Optional[Game] = self.current_mode.current_game

        # SALVATAGGIO STATO PARTITA
        if game and self.score_repository and self.current_user:
            try:
                self.score_repository.save_game_state(
                    user=self.current_user,
                    word=game.target_word,
                    attempts=game.attempts,
                    guesses=game.guesses,
                    is_over=game.is_over,
                    mode=type(self.current_mode).__name__,
                    language=self.language,
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Failed to save game state: %s", exc)

        # FINE PARTITA → salva score
        if game and game.is_over:
            score = self.get_score()

            logger.info(
                "Game finished | user=%s score=%s attempts=%s",
                self.current_user,
                score,
                game.attempts,
            )

            if self.score_repository and self.current_user:
                try:
                    self.score_repository.save_score(
                        user=self.current_user,
                        score=score,
                        attempts=game.attempts,
                    )
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.error("Failed to save score: %s", exc)

        return result

    def load_game(self, user: str) -> bool:
        """Carica una partita salvata se esiste."""
        if not self.score_repository:
            return False

        saved = self.score_repository.load_game_state(user)

        if not saved:
            return False

        game = Game(saved.word)
        game.attempts = saved.attempts
        game.is_over = saved.is_over
        game.guesses = saved.guesses

        if saved.mode == "ClassicMode":
            self.current_mode = ClassicMode(self.word_provider)
        else:
            self.current_mode = TrainingMode(self.word_provider)

        self.current_mode.current_game = game
        self.language = saved.language
        self.current_user = user

        logger.info("Game state loaded for user %s", user)

        return True
    
    def is_game_over(self) -> bool:
        """Controlla se la partita è terminata."""
        if self.current_mode is None:
            return True

        game: Optional[Game] = self.current_mode.current_game

        return game.is_over if game else True

    def get_attempts(self) -> int:
        """Restituisce il numero di tentativi."""
        if self.current_mode is None:
            logger.error("Attempts requested without active game.")
            raise RuntimeError("No active game")

        game: Optional[Game] = self.current_mode.current_game

        return game.attempts if game else 0

    def get_score(self) -> int:
        """Restituisce il punteggio per la modalità classica."""
        if isinstance(self.current_mode, ClassicMode):
            return self.current_mode.score
        return 0

    def get_current_user(self) -> Optional[str]:
        """Restituisce l'utente corrente."""
        return self.current_user

    def reset_game(self) -> None:
        """Resetta la sessione di gioco corrente."""
        logger.info("Resetting game session.")
        self.current_mode = None

    def get_target_word(self) -> str:
        """Restituisce la parola segreta da indovinare."""
        if (
            self.current_mode
            and hasattr(self.current_mode, "current_game")
            and self.current_mode.current_game
        ):
            return self.current_mode.current_game.target_word
        return ""

    def has_played_classic_today(self, user: str) -> bool:
        """Verifica se l'utente ha già giocato la partita classica di oggi."""
        if self.score_repository and user:
            return self.score_repository.has_played_today(user)
        return False

    def get_leaderboard(self) -> list[dict]:
        """
        Recupera i dati della classifica dal repository.
        Restituisce una lista vuota se il repository non è configurato
        o se la funzione non esiste ancora nel repository.
        """
        if self.score_repository:
            try:
                return self.score_repository.get_leaderboard_data()
            except AttributeError:
                logger.warning(
                    "get_leaderboard_data non implementato nel repository."
                )
        else:
            logger.warning("Score repository non configurato. Impossibile caricare la classifica.")
        return []
    