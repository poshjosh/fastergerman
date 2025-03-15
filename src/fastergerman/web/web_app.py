import logging
import os
from typing import List

from flask import Flask

from fastergerman.app import App
from fastergerman.game import FileQuestionsSource, AbstractGameStore, FileGameStore, Question
from fastergerman.web import GameService, WebService, AbstractGameSessionProvider

logger = logging.getLogger(__name__)


class GameSessionProvider(AbstractGameSessionProvider):
    def __init__(self, app_dir: str, questions: dict[str, List[Question]]):
        self.__app_dir = app_dir
        self.__questions = questions

    def create_store(self, session_id: str, trainer: str) -> AbstractGameStore:
        return FileGameStore.of_dir(os.path.join(self.__app_dir, session_id, trainer))

    def get_questions(self, trainer: str) -> List[Question]:
        return self.__questions.get(trainer, [])


class WebApp(App):
    def __init__(self, application: Flask, app_config_path: str = None, logging_config_path: str = None):
        super().__init__(app_config_path, logging_config_path)
        questions = FileQuestionsSource(self.config.get_questions_dir()).load_questions()
        session_provider = GameSessionProvider(self.config.get_app_dir(), questions)
        game_service = GameService(session_provider)

        self.web_service = WebService(self.config, game_service, questions.keys())

        App.add_shutdown_callback(self.web_service.close)

        self.application = application
        self.application.config.update(
            DEBUG=self.config.is_production() is False,
            SECRET_KEY=self.config.get_secret_key()
        )
        self.__started = False

    def is_started(self) -> bool:
        return self.__started

    def start(self) -> bool:
        if self.__started is True:
            return False
        logger.debug("Starting web app")
        self.__started = True
        self.application.run(
            host="0.0.0.0" if self.config.is_docker() is True else None,
            port=self.config.get_web_port())
        return True