import logging

from flask import Flask

from fastergerman.app import App
from fastergerman.game import QuestionsLoader
from fastergerman.web import GameService, WebService

logger = logging.getLogger(__name__)


class WebApp(App):
    def __init__(self, application: Flask, app_config_path: str = None, logging_config_path: str = None):
        super().__init__(app_config_path, logging_config_path)
        game_service = GameService(
            self.config.get_app_dir(),
            QuestionsLoader().load_questions(self.config.get_preposition_trainer_question_src()))

        self.web_service = WebService(self.config, game_service)

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