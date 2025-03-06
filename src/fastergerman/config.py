from typing import Union


class AppConfig:
    def __init__(self, config: dict[str, any]):
        self.__config = config if config is not None else {}

    def to_dict(self) -> dict[str, any]:
        return {**self.__config}

    def app(self) -> dict[str, any]:
        return self.__config.get('app', {})

    def get_app_name(self) -> str:
        return self.app()['name']

    def get_app_language(self, default: str or None) -> str or None:
        return self.app().get('language', default)

    def get_title(self, default: Union[str, None] = None) -> str:
        return self.app().get('title', default)

    def is_production(self) -> bool:
        return self.app().get('environment') == 'prod'

class WebAppConfig(AppConfig):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)
        self.__config = config if config is not None else {}

    def web(self) -> dict[str, any]:
        return self.__config.get('web', {})

    def get_web_port(self) -> int:
        return self.web().get('port', 5000)