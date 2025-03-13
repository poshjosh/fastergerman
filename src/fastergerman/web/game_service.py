import logging
import os
from typing import List, Callable

from werkzeug.exceptions import NotFound

from fastergerman.game import GameSession, GameTimer, Settings, Question, AbstractGameTimer, \
    AbstractGameStore, GameTimers, FileGameStore
from fastergerman.web import SESSION_ID, ACTION, GAME_SESSION
from fastergerman.web.request_data import TRAINER

logger = logging.getLogger(__name__)


class WebGameTimers(GameTimers):
    def __init__(self, get_question_display_time_millis: Callable[[], int]):
        super().__init__()
        self.__countdown_timer = GameTimer(1000)
        self.__next_ques_timer = None
        self.__get_question_display_time_millis = get_question_display_time_millis

    def get_countdown_timer(self) -> AbstractGameTimer:
        return self.__countdown_timer

    def get_next_ques_timer(self) -> AbstractGameTimer:
        if self.__next_ques_timer is None:
            logger.debug(f"Creating next question timer. Question display time millis: "
                         f"{self.__get_question_display_time_millis()}")
            self.__next_ques_timer = GameTimer(self.__get_question_display_time_millis())
        return self.__next_ques_timer


class WebGameSession(GameSession):
    def __init__(self, game_store: AbstractGameStore, questions: List[Question]):
        super().__init__(game_store, questions, WebGameTimers(self._get_question_display_time_millis))

    def _get_question_display_time_millis(self) -> int:
        return self.get_game().settings.question_display_time * 1000

class GameService:
    def __init__(self, app_dir: str, questions: dict[str, List[Question]]):
        self.__app_dir = app_dir
        self.__game_sessions = dict[str, GameSession]()
        self.__questions = questions

    def close(self):
        for session in self.__game_sessions.values():
            session.close()
        self.__game_sessions.clear()

    @staticmethod
    def _to_session_key(session_id: str, trainer: str) -> str:
        return f"{session_id}_{trainer}"

    def _create_session(self, session_id: str, trainer: str) -> GameSession:
        key = self._to_session_key(session_id, trainer)
        game_store = FileGameStore.of_dir(os.path.join(self.__app_dir, session_id))
        if trainer not in self.__questions.keys():
            raise NotFound(f"Trainer not found: {trainer}")
        self.__game_sessions[key] = WebGameSession(game_store, self.__questions[trainer])
        return self.__game_sessions[key]

    def _get_or_create_session(self, session_id: str, trainer: str) -> GameSession:
        key = self._to_session_key(session_id, trainer)
        if key not in self.__game_sessions.keys():
            self._create_session(session_id, trainer)
        return self.__game_sessions[key]

    def trainers(self, config: dict[str, any]) -> dict[str, any]:

        action = config.get(ACTION, None)
        logger.debug("Action: %s", action)

        if action == "update":
            game_session: GameSession = self._create_session(config[SESSION_ID], config[TRAINER])
        else:
            game_session: GameSession = self._get_or_create_session(config[SESSION_ID], config[TRAINER])

        if action == "start":
            game_session.start_game()
        elif action == "pause":
            game_session.pause_game()
        elif action == "next":
            game_session.handle_answer("") # timeout -> no answer -> wrong answer
            game_session.next_question()
        elif action == "answer":
            game_session.handle_answer(config.get("answer", ""))
            game_session.next_question()
        elif action == "update":
            self._update(config, game_session)

        config[GAME_SESSION] = game_session.to_dict()
        logger.debug("%s", game_session)

        return config

    @staticmethod
    def _update(config: dict[str, any], game_session: GameSession):
        game_to_load = config.get("game_to_load",game_session.get_game().name)
        save_game_as = config.get("save_game_as", game_to_load)
        logger.debug("Game to load: %s, Save game as: %s", game_to_load, save_game_as)

        game_session.create_new_game(game_to_load, Settings.of_dict(config))

        if save_game_as:
            game_session.save_game_as(save_game_as)
