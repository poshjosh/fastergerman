import logging
import random
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from enum import unique, Enum
from typing import List

from fastergerman.game import Question, Score, Settings, AbstractGameTimer, Game, GameFile
from fastergerman.i18n import START_GAME_PROMPT, GAME_COMPLETED_MESSAGE, I18n, DEFAULT_LANGUAGE_CODE

NO_GAME_NAME_SELECTION = "None"

logger = logging.getLogger(__name__)

class GameEventListener:
    def on_game_loaded(self, game: Game):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_game_started(self, game: Game):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_question(self, game: Game, question: Question):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_question_answered(self, game: Game, question: Question, answer: str):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_game_paused(self, game: Game):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_game_resumed(self, game: Game):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_game_completed(self, game: Game):
        """Subclasses should implement this method to handle the event."""
        pass
    def on_game_saved(self, game: Game):
        """Subclasses should implement this method to handle the event."""
        pass

@unique
class GameState(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    COMPLETED = 'COMPLETED'


class BaseGameSession:
    def __init__(self, game_file: GameFile, questions: List[Question]):
        self.__game_state = GameState.PENDING
        self.__previous_question: Question or None = None
        self.__previous_answer: str or None = None
        self.__current_question: Question or None = None
        self.__current_answer: str or None = None
        self.__game_event_listeners = []
        self.__lock = threading.Lock()
        self.__game_file = game_file
        self.__questions = [q for q in questions]  # use a copy
        self.__game: Game = self._create_new_game(questions=self.__questions)

    def close(self):
        logger.debug("Closing session")
        # TODO - Implement this method to save the game. Don't forget to log.
        raise NotImplementedError("close must be implemented by subclasses")

    def to_dict(self, lang_code: str) -> dict[str, any]:
        game_names = self.get_game_names()
        game_to_load = self.get_game_to_load()
        if not game_to_load and len(game_names) > 0:
            game_to_load = game_names[0]
        return {
            "is_running": self.__game_state == GameState.RUNNING,
            "game_names": game_names,
            "game_to_load": game_to_load,
            "settings": self.__game.settings.to_dict(),
            "score": str(self.__game.score),
            "question": {
                "current": self.to_ques_dict(lang_code, self.__current_question, self.__current_answer),
                "previous": self.to_ques_dict(lang_code, self.__previous_question, self.__previous_answer)
            },
            "questions_left": len(self.__game.questions)
        }

    @staticmethod
    def new_game_name():
        return f"Game_{datetime.today().strftime('%Y-%m-%d_%H%M%S')}"

    def load_game(self, game_name: str or None, settings: Settings or None = None):
        if game_name == NO_GAME_NAME_SELECTION:
            game_name = None

        if not game_name or self.__game_file.exists(game_name) is False:
            self.__game = self._create_new_game(game_name, settings, self.__questions)
        else:
            self.__game = self._load_existing_game(game_name, settings)

        logger.debug(f"Loaded game: {game_name} = {self.__game}")
        [e.on_game_loaded(self.__game) for e in self.__game_event_listeners]

    def update_settings_value(self, name: str, value: any):
        """
        Update the current game with the named setting.
        Will reset the score.
        :param name: The settings name
        :param value: The settings value
        :return: None
        """
        self.update_settings(self.__game.settings.with_value(name, value))

    def update_settings(self, settings: Settings):
        """
        Update the current game with the provided settings.
        Will reset the score.
        :param settings: The settings
        :return: None
        """
        self.__game = self.__game.with_settings(settings)

    def save_game_as(self, game_name: str):
        self.__game = self.__game.with_name(game_name)
        self.__game_file.save_game(self.__game)
        [e.on_game_saved(self.__game) for e in self.__game_event_listeners]

    def start_game(self):
        game_name = self.get_game_to_load()
        logger.debug("Starting game: %s", game_name)
        prev_state = self.__game_state
        self.__game_state = GameState.RUNNING
        self.load_game(game_name, self.__game.settings)
        if prev_state == GameState.PAUSED:
            [e.on_game_resumed(self.__game) for e in self.__game_event_listeners]
        else:
            [e.on_game_started(self.__game) for e in self.__game_event_listeners]

    def handle_answer(self, answer: str) -> bool:
        with self.__lock:
            # Updates score etc
            score_before = self.__game.score
            self.__previous_answer = self.__current_answer
            self.__current_answer = answer
            self.__game = self.__game.on_question_answer(self.__current_question, answer)
            logger.debug(f"Handled answer: {answer}. Score -> before: {score_before}, after: {self.__game.score}")
            self.__game_file.save_game(self.__game)
            [e.on_question_answered(self.__game, self.__current_question, answer)
             for e in self.__game_event_listeners]
            return self.__current_question.is_answer(answer)

    def pause_game(self):
        logger.debug(f"Pausing game: {self.__game.name} = {self.__game}")
        self.__previous_question = None
        self.__previous_answer = None
        self.__game_state = GameState.PAUSED
        # self.update_settings(self.__game.settings)
        [e.on_game_paused(self.__game) for e in self.__game_event_listeners]

    def add_game_event_listener(self, listener: GameEventListener):
        self.__game_event_listeners.append(listener)

    def get_game(self) -> Game:
        return self.__game

    def get_current_question(self) -> Question or None:
        return self.__current_question

    def get_current_answer(self) -> str or None:
        return self.__current_answer

    def get_previous_question(self) -> Question or None:
        return self.__previous_question

    def get_previous_answer(self) -> str or None:
        return self.__previous_answer

    def is_pending(self) -> bool:
        return self.__game_state == GameState.PENDING

    def is_running(self) -> bool:
        return self.__game_state == GameState.RUNNING

    def is_paused(self) -> bool:
        return self.__game_state == GameState.PAUSED

    def is_completed(self) -> bool:
        return self.__game_state == GameState.COMPLETED

    def get_game_to_load(self):
        return self.__game_file.read_game_to_load()

    def get_game_names(self) -> [str]:
        return self.__game_file.get_game_names()

    def get_max_questions(self) -> int:
        return len(self.__questions)

    def _create_new_game(self,
                         game_name: str or None = None,
                         settings: Settings or None = None,
                         questions: List[Question] or None = None) -> Game:
        if game_name is None:
            game_name = self.new_game_name()
        if settings is None:
            settings = Settings.of_dict({})
        if questions is None:
            questions = self.__questions
        return Game(game_name, settings, questions, Score(0, 0)).sync_with_settings()

    def _load_existing_game(self,
                            game_name: str or None = None,
                            settings: Settings or None = None) -> Game:
        self.__game = self.__game_file.load_game(game_name)
        if settings:
            return self.__game.with_settings(settings)
        else:
            return self.__game.sync_with_settings()

    def _next_question(self) -> Question or None:
        if self.is_running() is False:
            return None

        if len(self.__game.questions) == 0:
            self.pause_game()
            self.__game_state = GameState.COMPLETED
            [e.on_game_completed(self.__game) for e in self.__game_event_listeners]

            # Delete game
            self.__game_file.delete_game(self.__game.name)

            # Load default game, but start at next set of questions
            self.load_game(NO_GAME_NAME_SELECTION, self.__game.settings.next())
            return None

        self.__previous_question = self.__current_question
        self.__current_question = self._random_next_question()

        self.__previous_answer = self.__current_answer
        self.__current_answer = None

        [e.on_question(self.__game, self.__current_question) for e in self.__game_event_listeners]

        return self.__current_question

    def _random_next_question(self) -> Question or None:
        if len(self.__game.questions) == 0: # Should not happen
            raise ValueError("No questions left")
        if len(self.__game.questions) == 1:
            return self.__game.questions[0]
        next_question = None
        for _ in range(0, 5):
            next_question: Question or None = random.choice(self.__game.questions)
            if next_question != self.__current_question:
                break
        return next_question

    def to_ques_dict(self, language_code, question: Question = None, answer: str = None) -> dict[str, str]:
        translation = None
        choices = []
        correct_answer = None
        answer_correct = None
        if self.is_pending() is True:
            example = I18n.translate(language_code, START_GAME_PROMPT)
        elif self.is_completed() is False:
            example = question.example if question else None
            if self.__game.settings.display_translation is True:
                translation = question.translation if question else None
            choices = question.choices if question else []
            correct_answer = question.preposition if question else None
            answer_correct = question.is_answer(answer) is True if question else None
        else:
            example = I18n.translate(
                language_code, GAME_COMPLETED_MESSAGE).format(self.__game.score.to_percent())
        return {"example": example, "translation": translation,
                "choices": choices, "correct_answer": correct_answer,
                "answer": answer, "answer_correct": answer_correct}

    def __str__(self):
        return f"GameSession{self.to_dict(DEFAULT_LANGUAGE_CODE)}"


class GameTimers(ABC):
    @abstractmethod
    def get_countdown_timer(self) -> AbstractGameTimer:
        raise NotImplementedError("get_countdown_timer must be implemented by subclasses")

    @abstractmethod
    def get_next_ques_timer(self) -> AbstractGameTimer:
        raise NotImplementedError("get_next_ques_timer must be implemented by subclasses")


class GameSession(BaseGameSession):
    def __init__(self, game_file: GameFile, questions: List[Question], game_timers: GameTimers):
        super().__init__(game_file, questions)
        self.__game_timers = game_timers

    def handle_question(self, question: Question):
        """"
        Subclasses may implement this for further question handling
        """

    def get_countdown_timer(self) -> AbstractGameTimer:
        return self.__game_timers.get_countdown_timer()

    def get_next_ques_timer(self) -> AbstractGameTimer:
        return self.__game_timers.get_next_ques_timer()

    def to_dict(self, lang_code: str) -> dict[str, any]:
        data = super().to_dict(lang_code)
        data["countdown"] = int(self.get_countdown_timer().get_time_left_millis() / 1000)
        data["end_time"] = self.get_countdown_timer().get_end_time_millis()
        return data

    def start_game(self):
        was_paused = self.is_paused()
        super().start_game()
        if was_paused:
            self.handle_question(self.get_current_question())
            self.get_countdown_timer().resume()
            self.get_next_ques_timer().resume()
        else:
            self.next_question()

    def pause_game(self):
        super().pause_game()
        self.get_countdown_timer().stop()
        self.get_next_ques_timer().stop()

    def next_question(self, reset: bool = True) -> Question or None:
        logger.debug("Showing next question, triggered by timer: %1s", reset is False)
        if self.is_running() is False:
            self.pause_game()
            return None

        # Select random question
        question: Question = self._next_question()
        if question is None:
            return None

        self.get_countdown_timer().start(self.get_game().settings.question_display_time * 1000)
        if reset is True:
            self.get_next_ques_timer().start()

        self.handle_question(question)
        return question

    def handle_game_selection(self, game_name):
        self.load_game(game_name, self.get_game().settings)