import os
import uuid
from pathlib import Path

class Config:
    def __init__(self, config: dict[str, any]):
        self._config = config if config is not None else {}

    def to_dict(self) -> dict[str, any]:
        return {**self._config}

    @staticmethod
    def _path(val: str) -> str:
        return os.path.expanduser(os.path.expandvars(val))

class AppConfig(Config):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)

    def app(self) -> dict[str, any]:
        return self._config.get('app', {})

    def web(self) -> dict[str, any]:
        return self._config.get('web', {})

    def get_app_name(self) -> str:
        return self.app()['name']

    def get_app_version(self) -> str:
        return self.app()['version']

    def get_app_language(self, default: str = "en") -> str:
        env = os.environ.get("APP_LANGUAGE_CODE")
        return env if env else self.app().get('language-code', default)

    def is_production(self) -> bool:
        return 'prod' in self.get_app_profiles()

    def is_docker(self) -> bool:
        return "docker" in self.get_app_profiles()

    def get_app_profiles(self) -> [str]:
        env = os.environ.get("APP_PROFILES")
        val = env if env else self.app().get('profiles', 'dev')
        return val.split(',')

    def get_app_dir(self) -> str:
        env = os.environ.get("APP_DIR")
        val = env if env else self.app().get(
            'dir', os.path.join(Path.home(), f".{self.get_app_name().lower()}", f"v{self.get_app_version()}"))
        return self._path(val)

    def get_questions_dir(self) -> str:
        env = os.environ.get("APP_QUESTIONS_DIR")
        return self._path(env if env else self.app()['questions']['dir'])

    def get_translations_dir(self) -> str:
        env = os.environ.get("APP_TRANSLATIONS_DIR")
        return self._path(env if env else self.app()['translations']['dir'])

    def get_web_port(self) -> int:
        env = os.environ.get("APP_PORT")
        return env if env else self.web().get('port', 5000)

    def get_secret_key(self) -> str:
        secret_key = os.environ.get('APP_SECRET_KEY')
        if secret_key:
            return secret_key
        if self.is_production() is True:
            raise ValueError('APP_SECRET_KEY is required')
        else:
            return str(uuid.uuid4().hex)

class LoggingConfig(Config):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)

    def get_filename(self) -> str:
        return self._path(self._config["handlers"]["file"]["filename"])

