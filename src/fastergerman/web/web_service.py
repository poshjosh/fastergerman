import logging

from fastergerman.config import AppConfig
from fastergerman.i18n import I18n, DEFAULT_LANGUAGE_CODE
from fastergerman.web import LANG_CODE, GameService, RequestData

logger = logging.getLogger(__name__)

class WebService:
    def __init__(self, app_config: AppConfig, game_service: GameService, trainer_types: [str]):
        self.__game_service = game_service
        self.__default_page_variables = {
            "app": {
                "name": app_config.get_app_name(),
                "is_production": app_config.is_production(),
                "trainer_types": trainer_types  #[str(e) for e in trainer_types]
            }
        }

    def close(self):
        self.__game_service.close()

    def default(self, page_variables: dict[str, any] = None) -> dict[str, str]:
        return self._with_default_page_variables(page_variables)

    def trainers(self, page_variables: dict[str, any]) -> dict[str, any]:
        return self._with_default_page_variables(self.__game_service.trainers(page_variables))

    def _with_default_page_variables(self, variables: dict[str, any] = None):
        if variables is None:
            variables = {}
        lang_code = variables.get(LANG_CODE, DEFAULT_LANGUAGE_CODE)
        variables["i18n"] = {
            "supported_languages": I18n.get_supported_languages(),
            "dir": I18n.get_dir(lang_code),
            "lang_code": lang_code,
            "t": I18n.get_translations(lang_code)
        }

        RequestData.sync_to_session(variables)

        for key, value in self.__default_page_variables.items():
            if key not in variables.keys():
                variables[key] = value

        return variables

    def get_game_service(self) -> GameService:
        return self.__game_service