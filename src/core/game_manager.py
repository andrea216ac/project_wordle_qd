"""Game manager coordina le sessioni di gioco."""

import json
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
        """Inizia un nuovo gioco."""
        self.language = language
        self.current_user = user

        # =========================
        # MODALITÀ CLASSICA
        # =========================
        if mode == "classic":

            # 1. RIPRISTINO PARTITA SALVATA
            if self.score_repository and user:
                saved_state_str = self.score_repository.load_game_state(user)

                if saved_state_str:
                    try:
                        state = json.loads(saved_state_str)

                        if (
                            state.get("mode") == "classic"
                            and state.get("language") == language
                        ):
                            logger.info("Ripristino partita salvata per %s", user)

                            self.current_mode = ClassicMode(self.word_provider)
                            self.current_mode.start_game(language)

                            game = self.current_mode.current_game

                            # Ripristino dati
                            assert game is not None
                            game.target_word = state.get(
                                "target_word", game.target_word
                            )
                            game.attempts = state.get("attempts", 0)
                            game.guesses = state.get("guesses", [])
                            game.is_over = state.get("is_over", False)

                            return

                    except (json.JSONDecodeError, KeyError) as exc:
                        logger.error("Errore ripristino partita: %s", exc)

            # 2. CONTROLLO GIOCO GIÀ FATTO
            if self.score_repository and user:
                if self.score_repository.has_played_today(user):
                    logger.warning("User %s already played today's classic game", user)
                    raise RuntimeError("Classic mode already played today")

            # 3. NUOVA PARTITA
            self.current_mode = ClassicMode(self.word_provider)
            self.current_mode.start_game(language)

        # =========================
        # MODALITÀ TRAINING
        # =========================
        elif mode == "training":
            self.current_mode = TrainingMode(self.word_provider)
            self.current_mode.start_game(language)

        else:
            logger.error("Invalid mode requested: %s", mode)
            raise ModeError(f"Invalid mode: {mode}")

        logger.info(
            "Game started | user=%s mode=%s language=%s",
            self.current_user,
            mode,
            language,
        )

    def submit_guess(self, guess: str) -> List[str]:
        """Invia un tentativo alla partita."""
        if self.current_mode is None:
            logger.error("Attempted guess without active game.")
            raise RuntimeError("No active game")

        # VALIDAZIONE PAROLA
        assert self.language is not None
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

        # =========================
        # SALVATAGGIO STATO (JSON)
        # =========================
        if game and self.score_repository and self.current_user:
            try:
                state_dict = {
                    "target_word": game.target_word,
                    "attempts": game.attempts,
                    "guesses": getattr(game, "guesses", []),
                    "is_over": game.is_over,
                    "language": self.language,
                    "mode": (
                        "classic"
                        if isinstance(self.current_mode, ClassicMode)
                        else "training"
                    ),
                }

                self.score_repository.save_game_state(
                    self.current_user,
                    json.dumps(state_dict),
                )

            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Failed to save game state: %s", exc)

        # =========================
        # FINE PARTITA
        # =========================
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

                    # reset salvataggio
                    self.score_repository.save_game_state(self.current_user, "")

                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.error("Failed to save score: %s", exc)

        return result

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
        """Restituisce la parola segreta."""
        if (
            self.current_mode
            and hasattr(self.current_mode, "current_game")
            and self.current_mode.current_game
        ):
            return self.current_mode.current_game.target_word
        return ""

    def has_played_classic_today(self, user: str) -> bool:
        """Verifica se l'utente ha già giocato oggi."""
        if self.score_repository and user:
            return self.score_repository.has_played_today(user)
        return False

    def get_leaderboard(self) -> list[dict]:
        """Restituisce la classifica."""
        if self.score_repository:
            try:
                return self.score_repository.get_leaderboard_data()
            except AttributeError:
                logger.warning("get_leaderboard_data non implementato nel repository.")
        else:
            logger.warning("Score repository non configurato.")
        return []
