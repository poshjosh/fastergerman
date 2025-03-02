import logging

from fastergerman.config import AppConfig
from fastergerman.game import GameSession
from fastergerman.i18n import I18n
from fastergerman.web import LANG_CODE, GameService, ACTION

logger = logging.getLogger(__name__)

class WebService:
    def __init__(self, app_config: AppConfig, game_service: GameService):
        self.__game_service = game_service
        self.__default_page_variables = {
            'app_name': app_config.get_app_name(),
            'title': app_config.get_title(),
            'heading': app_config.get_title(),
            'supported_languages': I18n.get_supported_languages()
        }

    def close(self):
        self.__game_service.close()

    def index(self, page_variables: dict[str, any] = None) -> dict[str, str]:
        return self._with_default_page_variables(page_variables)

    def preposition_trainer(self, page_variables: dict[str, any]) -> dict[str, any]:
        return self.with_game_session(
            page_variables, self.__game_service.preposition_trainer(page_variables))

    def with_game_session(
            self, page_variables: dict[str, any], game_session: GameSession) -> dict[str, any]:

        page_variables["game_session"] = game_session.to_dict(page_variables[LANG_CODE])
        logger.debug("%s", game_session)

        return self._with_default_page_variables(page_variables)

    def _with_default_page_variables(self, variables: dict[str, any] = None):
        if variables and LANG_CODE in variables:
            variables["i18n"] = I18n.get_translations(variables[LANG_CODE])
        if variables is None:
            variables = {}
        for key, value in self.__default_page_variables.items():
            if key not in variables.keys():
                variables[key] = value
        return variables

    def get_game_service(self) -> GameService:
        return self.__game_service