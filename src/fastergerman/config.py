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

class ChatModelConfig(Config):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)

    def get_name(self) -> str:
        env = os.environ.get("APP_CHAT_MODEL_NAME")
        return env if env else self._config.get('name', 'gpt-4o-mini')

    def get_provider(self) -> str:
        env = os.environ.get("APP_CHAT_MODEL_PROVIDER")
        return env if env else self._config.get('provider', 'openai')

    def get_api_key(self) -> str or None:
        env = os.environ.get("APP_CHAT_MODEL_API_KEY")
        return env if env else self._config.get('api_key')

class ChatConfig(Config):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)
        self.__model_config = ChatModelConfig(self._config.get('model', {}))

    def model(self) -> ChatModelConfig:
        return self.__model_config

    def get_history_max_tokens(self) -> int:
        env = os.environ.get("APP_CHAT_HISTORY_MAX_TOKENS")
        return int(env) if env else self._config.get('history_max_tokens', 1024)

    def get_prompt(self) -> str or None:
        env = os.environ.get("APP_CHAT_PROMPT")
        return env if env else self._config.get('prompt')

    def is_disabled(self) -> bool:
        env = os.environ.get("APP_CHAT_DISABLED")
        return env if env else self._config.get('disabled', False)

    def get_ratelimit_permits(self) -> int:
        env = os.environ.get("APP_CHAT_RATELIMIT_PERMITS")
        return int(env) if env else self._config.get("ratelimit", {}).get('permits', -1)

    def get_ratelimit_duration(self) -> int:
        env = os.environ.get("APP_CHAT_RATELIMIT_DURATION")
        return int(env) if env else self._config.get("ratelimit", {}).get('duration', -1)

class AppConfig(Config):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)
        self.__chat_config = ChatConfig(self._app().get('chat', {}))

    def chat(self) -> ChatConfig:
        return self.__chat_config

    def get_app_name(self) -> str:
        return self._app()['name']

    def get_app_version(self) -> str:
        return self._app()['version']

    def get_app_language(self, default: str = "en") -> str:
        env = os.environ.get("APP_LANGUAGE_CODE")
        return env if env else self._app().get('language-code', default)

    def is_production(self) -> bool:
        return 'prod' in self.get_app_profiles()

    def is_docker(self) -> bool:
        return "docker" in self.get_app_profiles()

    def get_app_profiles(self) -> [str]:
        env = os.environ.get("APP_PROFILES")
        val = env if env else self._app().get('profiles', 'dev')
        return val.split(',')

    def get_app_dir(self) -> str:
        env = os.environ.get("APP_DIR")
        val = env if env else self._app().get(
            'dir', os.path.join(Path.home(), f".{self.get_app_name().lower()}", f"v{self.get_app_version()}"))
        return self._path(val)

    def get_questions_dir(self) -> str:
        env = os.environ.get("APP_QUESTIONS_DIR")
        return self._path(env if env else self._app()['questions']['dir'])

    def get_translations_dir(self) -> str:
        env = os.environ.get("APP_TRANSLATIONS_DIR")
        return self._path(env if env else self._app()['translations']['dir'])

    def get_web_port(self) -> int:
        env = os.environ.get("APP_PORT")
        return env if env else self._web().get('port', 5000)

    def get_secret_key(self) -> str:
        secret_key = os.environ.get('APP_SECRET_KEY')
        if secret_key:
            return secret_key
        if self.is_production() is True:
            raise ValueError('APP_SECRET_KEY is required')
        else:
            return str(uuid.uuid4().hex)

    def _app(self) -> dict[str, any]:
        return self._config.get('app', {})

    def _web(self) -> dict[str, any]:
        return self._config.get('web', {})

class LoggingConfig(Config):
    def __init__(self, config: dict[str, any]):
        super().__init__(config)

    def get_filename(self) -> str:
        return self._path(self._config["handlers"]["file"]["filename"])

