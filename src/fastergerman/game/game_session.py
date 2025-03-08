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

INITIAL_GAME_NAME = "Game 1"

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
        self.__current_question: Question or None = None
        self.__current_answer: str or None = None
        self.__game_to_load = None
        self.__game_event_listeners = []
        self.__lock = threading.Lock()
        self.__game_file = game_file
        self.__questions = [q for q in questions]  # use a copy
        self.__game: Game = self._get_default_game(self.__questions)

    def close(self):
        logger.debug("Closing session")
        # TODO - Implement this method to save the game. Don't forget to log.
        raise NotImplementedError("close must be implemented by subclasses")

    def to_dict(self, lang_code: str, last_answer_correct: bool = None,
                question: Question = None) -> dict[str, any]:
        if question is None:
            question = self.__current_question
        game_names = self.get_game_names_or_default()
        return {
            "is_running": self.__game_state == GameState.RUNNING,
            "game_names": game_names,
            "game_to_load": self.__game_to_load if self.__game_to_load else game_names[0],
            "settings": self.__game.settings.to_dict(),
            "score": str(self.__game.score),
            "question": self._get_question(lang_code, question),
            "question_options": question.choices if self.__current_question else [],
            "questions_left": len(self.__game.questions),
            "last_answer_correct": last_answer_correct
        }

    def load_default_game(self, settings: Settings):
        self.load_game(NO_GAME_NAME_SELECTION, settings)
        
    def load_game(self, game_name: str or None, settings: Settings):
        """
        Load a game with the specified settings.
        If the game was loaded from file, the provided settings will be ignored.
        """
        if game_name:
            if game_name == NO_GAME_NAME_SELECTION:  # reset
                self.__game = self._get_default_game(
                    self.__questions,
                    f"Game_{datetime.today().strftime('%Y-%m-%d_%H%M%S')}",
                    settings)
            else:
                self.__game = self.__game_file.load_game(game_name)
            self.set_game_to_load(self.__game.name)
        else:
            self.__game = self._get_default_game(self.__questions, settings=settings)
            if self.__game_to_load == INITIAL_GAME_NAME or not self.__game_to_load:
                self.set_game_to_load(self.__game.name)
        [e.on_game_loaded(self.__game) for e in self.__game_event_listeners]

    def update_settings_value(self, name: str, value: any):
        self.update_settings(self.__game.settings.with_value(name, value))

    def update_settings(self, settings: Settings):
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
            self.__current_answer = answer
            self.__game = self.__game.on_question_answer(self.__current_question, answer)
            logger.debug(f"Handled answer: {answer}. Score -> before: {score_before}, after: {self.__game.score}")
            self.__game_file.save_game(self.__game)
            [e.on_question_answered(self.__game, self.__current_question, answer)
             for e in self.__game_event_listeners]
            return self.__current_question.is_answer(answer)

    def pause_game(self):
        logger.debug(f"Pausing game: {self.__game.name} = {self.__game}")
        self.__game_state = GameState.PAUSED
        self.update_settings(self.__game.settings)
        [e.on_game_paused(self.__game) for e in self.__game_event_listeners]

    def add_game_event_listener(self, listener: GameEventListener):
        self.__game_event_listeners.append(listener)

    def get_game(self) -> Game:
        return self.__game

    def get_current_question(self) -> Question or None:
        return self.__current_question

    def get_current_answer(self) -> str or None:
        return self.__current_answer

    def set_game_to_load(self, value: str):
        self.__game_to_load = value

    def is_pending(self) -> bool:
        return self.__game_state == GameState.PENDING

    def is_running(self) -> bool:
        return self.__game_state == GameState.RUNNING

    def is_paused(self) -> bool:
        return self.__game_state == GameState.PAUSED

    def is_completed(self) -> bool:
        return self.__game_state == GameState.COMPLETED

    def get_game_to_load(self):
        return self.__game_file.get_game_to_load()

    def get_game_to_load_or_default(self):
        last_saved_game = self.__game_file.get_game_to_load()
        return INITIAL_GAME_NAME if not last_saved_game else last_saved_game

    def get_game_names(self) -> [str]:
        return self.__game_file.get_game_names()

    def get_game_names_or_default(self) -> [str]:
        game_names = self.__game_file.get_game_names()
        if len(game_names) == 0:
            game_names.append(NO_GAME_NAME_SELECTION)
        return game_names

    def get_max_questions(self) -> int:
        return len(self.__questions)

    def _get_default_game(self,
                          questions: List[Question],
                          game_name: str = INITIAL_GAME_NAME,
                          settings: Settings = Settings.of_dict({})) -> Game:
        offset = settings.start_at_question_number
        limit = settings.max_number_of_questions
        return Game(game_name, settings, self._get_questions(questions, offset, limit), Score(0, 0))

    @staticmethod
    def _get_questions(questions: List[Question], first_question: int = 0, max_questions: int = None) -> List[Question]:
        number_of_ques = len(questions)
        if max_questions is None:
            max_questions = number_of_ques
        last_question = first_question + max_questions
        if last_question > number_of_ques:
            last_question = number_of_ques
        return questions[first_question:last_question]

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
            self.load_default_game(self.__game.settings.next())
            return None

        self.update_settings(self.__game.settings)

        # Select random question
        next_question: Question = random.choice(self.__game.questions)

        if next_question == self.__current_question:
            # If the same question is selected, try once more
            next_question: Question = random.choice(self.__game.questions)

        self.__current_question = next_question

        [e.on_question(self.__game, next_question) for e in self.__game_event_listeners]

        return next_question

    def _get_question(self, language_code, question: Question = None) -> dict[str, str]:
        if question is None:
            question = self.__current_question
        translation = ""
        if self.is_pending() is True:
            example = I18n.translate(language_code, START_GAME_PROMPT)
        elif self.is_completed() is False:
            example = question.example
            if self.__game.settings.display_translation is True:
                translation = question.translation
        else:
            example = I18n.translate(
                language_code, GAME_COMPLETED_MESSAGE).format(self.__game.score.to_percent())
        return {"example": example, "translation": translation}

    def __str__(self):
        return f"GameSession{self.to_dict(DEFAULT_LANGUAGE_CODE)}"


class GameTimers(ABC):
    @abstractmethod
    def get_countdown_timer(self) -> AbstractGameTimer:
        raise NotImplementedError("get_countdown_timer must be implemented by subclasses")

    @abstractmethod
    def get_next_ques_timer(self) -> AbstractGameTimer:
        raise NotImplementedError("get_next_ques_timer must be implemented by subclasses")


class GameSession(BaseGameSession, GameTimers):
    def __init__(self, game_file: GameFile, questions: List[Question]):
        super().__init__(game_file, questions)

    @abstractmethod
    def get_countdown_timer(self) -> AbstractGameTimer:
        raise NotImplementedError("get_countdown_timer must be implemented by subclasses")

    @abstractmethod
    def get_next_ques_timer(self) -> AbstractGameTimer:
        raise NotImplementedError("get_next_ques_timer must be implemented by subclasses")

    def handle_question(self, question: Question):
        raise NotImplementedError("handle_question must be implemented by subclasses")

    def to_dict(self, lang_code: str, last_answer_correct: bool = None,
                question: Question = None) -> dict[str, any]:
        data = super().to_dict(lang_code, last_answer_correct, question)
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

        countdown_timed_out = self.get_countdown_timer().is_timed_out()
        logger.debug("Is countdown timed out: %1s, %2s",
                     countdown_timed_out, self.get_countdown_timer())

        if countdown_timed_out is True:
            # timeout -> no answer -> wrong answer
            self.handle_answer("")

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
        self.set_game_to_load(game_name)
        self.load_game(game_name, self.get_game().settings)