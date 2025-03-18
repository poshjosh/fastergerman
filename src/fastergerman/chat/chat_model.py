import dataclasses
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class ChatModelData:
    name: str
    provider: str or None
    api_key: str or None

    @staticmethod
    def of_dict(data: dict[str, str]) -> 'ChatModelData':
        return ChatModelData(data["name"], data.get("provider"), data.get("api_key"))

    def to_dict(self):
        return dataclasses.asdict(self)

#https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard#/
class ChatModelProvider:
    def __init__(self, config: ChatModelData = None):
        self.__default_config: ChatModelData = config
        self.__supported_models = {
            "llama3-8b-8192": "groq",
            "gpt-4o-mini": "openai",
            "claude-3-5-sonnet-latest": "anthropic",
            "command-r-plus": "cohere",
            "meta/llama3-70b-instruct": "nvidia",
            "grok-2": "xai"
        }

    def get_supported_models(self) -> dict[str, str]:
        return {**self.__supported_models}

    def create_model(self, config: ChatModelData = None):
        if config is None:
            config = self.__default_config
        model_name = config.name
        provider = config.provider
        if not provider:
            provider = self.__supported_models.get(model_name)
        api_key = config.api_key
        if api_key:
            os.environ[self._api_key_env_name_for_provider(provider)] = api_key
        from langchain.chat_models import init_chat_model
        return init_chat_model(model_name, model_provider=provider)

    @staticmethod
    def _api_key_env_name_for_provider(provider: str):
        return f"{provider.upper()}_API_KEY"
