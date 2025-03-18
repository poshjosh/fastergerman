import dataclasses
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence
from typing_extensions import Annotated, TypedDict, NotRequired

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, trim_messages
from langgraph.graph.message import add_messages

from fastergerman.chat import ChatModelProvider, ChatModelData
from fastergerman.config import ChatConfig
from fastergerman.i18n import I18n, UNEXPECTED_ERROR, LLM_NOT_FOUND, TOO_MANY_REQUESTS, \
    CHAT_DISABLED, PROVIDE_CHAT_MODEL_API_KEY
from fastergerman.web import CHAT_REQUEST, SESSION_ID, LANG_CODE, CHAT_MODEL_NAME, \
    CHAT_MODEL_PROVIDER, CHAT_MODEL_API_KEY

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChatMessage:
    content: str
    author: str
    timestamp: float
    def to_dict(self):
        return dataclasses.asdict(self)

@dataclass(frozen=True)
class ChatRequest:
    session_id: str
    lang_name: str
    lang_code: str
    query: str
    model: ChatModelData

    @staticmethod
    def of(data: dict[str, str]) -> 'ChatRequest':
        lang_code = data[LANG_CODE]
        name = data.get(CHAT_MODEL_NAME)
        provider = data.get(CHAT_MODEL_PROVIDER)
        model = None if not name else ChatModelData(name, provider, data[CHAT_MODEL_API_KEY])
        return ChatRequest(
            data[SESSION_ID], I18n.get_english_name_for_code(lang_code), lang_code,
            data[CHAT_REQUEST], model)

    def with_model_if_not_set(self, model_data: ChatModelData) -> 'ChatRequest':
        if self.model:
            return self
        return ChatRequest(self.session_id, self.lang_name, self.lang_code, self.query, model_data)

    def to_dict(self):
        return dataclasses.asdict(self)


class MessageState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str
    model_data: ChatModelData
    limit_exceeded: NotRequired[bool]


class AbstractChatService(ABC):
    @abstractmethod
    def chat(self, request: ChatRequest) -> [ChatMessage]:
        raise NotImplementedError()

    @abstractmethod
    def chat_stream(self, request: ChatRequest):
        raise NotImplementedError()

    @abstractmethod
    def get_model_provider(self) -> ChatModelProvider:
        raise NotImplementedError()

class MessageConverter:

    def get_datetime_format(self):
        return '%Y-%m-%dT%H:%M:%S.%f%z'

    def to_message_input(self, request: ChatRequest) -> MessageState:
        dt_str = datetime.now(timezone.utc).strftime(self.get_datetime_format()).replace("+0000", "Z")
        return {
            "messages": [HumanMessage(
                request.query, response_metadata={"created_at": dt_str})],
            "language": request.lang_name,
            "model_data": request.model
        }

    def to_message_output(self, message: BaseMessage) -> ChatMessage:
        human_author = isinstance(message, HumanMessage) is True
        author = "me" if human_author is True else self._message_model(message, "ai")
        return ChatMessage(message.content, author, self._message_timestamp(message))

    def _message_timestamp(self, message: BaseMessage):
        if message.response_metadata and "created_at" in message.response_metadata:
            return datetime.strptime(message.response_metadata["created_at"], self.get_datetime_format()).timestamp()
        return datetime.now().timestamp()

    def _message_model(self, message: BaseMessage, default: str):
        return message.response_metadata.get("model", default) if message.response_metadata else default

class LangchainChatService(AbstractChatService):
    @staticmethod
    def of(config: ChatConfig, request_to_state_converter: MessageConverter) -> AbstractChatService:
        model_data = LangchainChatService._model_data(config)
        return LangchainChatService(ChatModelProvider(model_data), config, request_to_state_converter)

    def __init__(self, model_provider: ChatModelProvider, config: ChatConfig,
                 request_to_state_converter: MessageConverter):
        super().__init__()
        self.__model_provider = model_provider
        self.__config = config
        self.__default_model_data = self._model_data(config)
        self.__message_converter = request_to_state_converter
        self.__models = {}
        self.__message_trimmers = {}

        self.__prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", config.get_prompt()),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Define a new graph
        workflow = StateGraph(state_schema=MessageState)

        # Define the (single) node in the graph
        workflow.add_edge(START, "model")
        workflow.add_node("model", self._call_model)

        # Add memory
        memory = MemorySaver()
        self.__chat_workflow = workflow.compile(checkpointer=memory)

    def get_model_provider(self) -> ChatModelProvider:
        return self.__model_provider

    def chat(self, request: ChatRequest) -> [ChatMessage]:
        request = request.with_model_if_not_set(self.__default_model_data)
        response = self.__chat_workflow.invoke(
            self.__message_converter.to_message_input(request),
            {"configurable": {"thread_id": request.session_id}}
        )
        return [self.__message_converter.to_message_output(e) for e in response["messages"]]

    def chat_stream(self, request: ChatRequest):
        request = request.with_model_if_not_set(self.__default_model_data)
        for message, metadata in self.__chat_workflow.stream(
                self.__message_converter.to_message_input(request),
                {"configurable": {"thread_id": request.session_id}},
                stream_mode="messages"):
            logger.debug(f"Message: {message}\nMetadata: {metadata}")
            # Message: content='!' additional_kwargs={} response_metadata={} id='run-49644c52-8703-4549-9a10-5b1a105125eb'
            # Metadata: {'thread_id': 'a7dfa06462dd4c1b92ba0ac40f97ae9f', 'langgraph_step': 1, 'langgraph_node': 'model', 'langgraph_triggers': ['start:model'], 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:1f773578-877a-d513-fae0-f38635c933d3', 'checkpoint_ns': 'model:1f773578-877a-d513-fae0-f38635c933d3', 'ls_provider': 'ollama', 'ls_model_name': 'llama3.1', 'ls_model_type': 'chat', 'ls_temperature': None}
            if isinstance(message, HumanMessage) is True or isinstance(message, AIMessage) is True:
                yield self.__message_converter.to_message_output(message)

    def _call_model(self, state: MessageState):
        logger.debug(f"Chat message state: {state}")
        model_data = state["model_data"]
        if self.__config.is_disabled() is True:
            lang_code = I18n.get_code_for_english_name(state["language"])
            last_message_content = I18n.translate(lang_code, CHAT_DISABLED)
            ai_message = AIMessage(f"{last_message_content}")
        elif state.get("limit_exceeded") is True:
            lang_code = I18n.get_code_for_english_name(state["language"])
            last_message_content = I18n.translate(lang_code, TOO_MANY_REQUESTS)
            ai_message = AIMessage(f"{last_message_content}")
        elif model_data.provider == "echo":
            last_message = state["messages"][-1]
            ai_message = AIMessage(f"echo: {last_message.content}")
        else:
            model = self._get_model(model_data)
            messages = self._filter_messages(model, state)
            try:
                ai_message: AIMessage = model.invoke(messages)
            except Exception as ex:
                logger.warning(f"Error invoking model: {model.name}. {ex}")
                ai_message = self._handle_model_response_error(ex, model_data.name, state["language"])
        logger.debug(f"Chat response: {ai_message}")
        return {"messages": ai_message}

    @staticmethod
    def _model_data(config: ChatConfig):
        m_cfg = config.model()
        return ChatModelData(m_cfg.get_name(), m_cfg.get_provider(), m_cfg.get_api_key())

    def _get_model(self, config: ChatModelData = None):
        key = f"{config.provider}.{config.name}"
        val = self.__models.get(key)
        if val is None:
            val = self.__model_provider.create_model(config)
            self.__models[key] = val
        return val

    def _filter_messages(self, model, state: MessageState):
        model_data = state["model_data"]
        try:
            messages = self._get_message_trimmer(model, model_data).invoke(state["messages"])
        except NotImplementedError as ex:
            logger.warning(f"Trimming of messages not implemented by model: {model.name}. {ex}")
            messages = state["messages"]
        if self.__prompt_template:
            return self.__prompt_template.invoke({"messages": messages, **state})
        return messages

    def _get_message_trimmer(self, model, config: ChatModelData):
        key = f"{config.provider}.{config.name}"
        val = self.__message_trimmers.get(key)
        if val is None:
            val = self._create_message_trimmer(model)
            self.__message_trimmers[key] = val
        return val

    def _create_message_trimmer(self, model):
        return trim_messages(
            max_tokens=self.__config.get_history_max_tokens(),
            strategy="last",
            token_counter=model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

    @staticmethod
    def _handle_model_response_error(ex: Exception, model_name: str, language: str) -> AIMessage:
        lang_code = I18n.get_code_for_english_name(language)
        class_name = ex.__class__.__name__
        if "notfound" in class_name.lower():
            message = f"{I18n.translate(lang_code, LLM_NOT_FOUND)}: {model_name}"
        elif "ratelimit" in class_name.lower():
            message_line_1 = I18n.translate(lang_code, TOO_MANY_REQUESTS)
            message_line_2 = I18n.translate(lang_code, PROVIDE_CHAT_MODEL_API_KEY)
            message = f"{message_line_1}. {message_line_2}"
        else:
            message = f"{I18n.translate(lang_code, UNEXPECTED_ERROR)}: {model_name}"
        return AIMessage(message)

