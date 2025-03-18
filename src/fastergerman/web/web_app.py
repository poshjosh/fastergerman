import logging

from flask import Flask

from fastergerman.app import App
from fastergerman.chat import LangchainChatService, ChatRequest
from fastergerman.chat.chat_service import MessageState, MessageConverter
from fastergerman.game import FileQuestionsSource
from fastergerman.web import GameService, WebService, RateLimiter

logger = logging.getLogger(__name__)


class MessageConverterImpl(MessageConverter):
    def __init__(self, rate_limiter: RateLimiter, default_llm_api_key: str):
        self.__rate_limiter = rate_limiter
        self.__default_llm_api_key = default_llm_api_key

    def to_message_input(self, request: ChatRequest) -> MessageState:
        message_state = super().to_message_input(request)
        if request.model.api_key != self.__default_llm_api_key: # user provided own api key
            return message_state
        if self.__rate_limiter.is_within_limit(request.session_id) is False:
            message_state["limit_exceeded"] = True
        return message_state


class WebApp(App):
    def __init__(self, application: Flask, app_config_path: str = None, logging_config_path: str = None):
        super().__init__(app_config_path, logging_config_path)

        questions = FileQuestionsSource(self.config.get_questions_dir()).load_questions()
        game_service = GameService.of(self.config.get_app_dir(), questions)

        state_converter = MessageConverterImpl(
            RateLimiter(self.config.chat().get_ratelimit_permits(),
                        self.config.chat().get_ratelimit_duration()),
            self.config.chat().model().get_api_key())
        chat_service = LangchainChatService.of(self.config.chat(), state_converter)
        self.web_service = WebService(self.config, game_service, questions.keys(), chat_service)

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