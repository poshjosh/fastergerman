import logging
import uuid
from datetime import timezone
from typing import Union

from flask import session

from fastergerman.game import NO_GAME_NAME_SELECTION
from fastergerman.i18n import I18n, REQUIRED, SAVE_GAME_AS, INVALID, \
    GAME_TO_LOAD

logger = logging.getLogger(__name__)

LANG_CODE = "lang_code"
SESSION_ID = "session_id"
ACTION = "action"
GAME_SESSION = "game_session"
TRAINER = "trainer"
TRAINER_TYPES = "trainer_types"
TIMEZONE = "timezone"

CHAT_REQUEST = "chat_request"
CHAT_MODEL_NAME = "chat_model_name"
CHAT_MODEL_PROVIDER = "chat_model_provider"
CHAT_MODEL_API_KEY = "chat_model_api_key"

class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class RequestData:
    @staticmethod
    def get_list(request, key: str, result_if_none: [str]) -> [str]:
        values = request.args.to_dict(flat=False).get(key)
        if not values:
            values = request.form.getlist(key)
        return values if values else result_if_none

    @staticmethod
    def get(request, key: str, result_if_none: any = None) -> Union[str, None]:
        val = request.args.get(key)
        if not val:
            val = request.form.get(key)
        return result_if_none if not val else val

    @staticmethod
    def collect(request) -> dict[str, any]:

        request_data = {**dict(request.form), **dict(request.args)}

        logger.debug(f"Input form data: {request_data}")
        request_data = RequestData.strip_values(request_data)

        session[SESSION_ID] = session.get(SESSION_ID, str(uuid.uuid4().hex))
        session[LANG_CODE] = request_data.get(LANG_CODE, RequestData.get_language_code(request))
        logger.debug(f"Session: {session.items()}")
        for k, v in session.items():
            request_data[k] = v

        logger.debug(f"Output request data: {request_data}")
        return request_data

    @staticmethod
    def trainers(request) -> dict[str, any]:
        request_data = RequestData.collect(request)
        RequestData.validate_form_data(request_data)
        RequestData.require_save_game_as_is_not_reserved_name(request_data)
        return request_data

    @staticmethod
    def get_timezone(request, default: str = str(timezone.utc)) -> str:
        return RequestData.get(request, TIMEZONE, session.get(TIMEZONE, default))

    @staticmethod
    def get_language_code(request, default: str = I18n.get_default_language_code()) -> str:
        return session.get(LANG_CODE, RequestData._request_lang_code(request, default))

    @staticmethod
    def _request_lang_code(request, default: str = I18n.get_default_language_code()) -> str:
        supported_lang_codes = I18n.get_supported_language_codes()
        best_match = request.accept_languages.best_match(supported_lang_codes)
        return best_match if best_match and I18n.is_supported(best_match) else default

    @staticmethod
    def strip_values(data: dict[str, any]):
        for k, v in data.items():
            v = v.strip() if isinstance(v, str) else v
            data[k] = v
        return data

    @staticmethod
    def validate_form_data(data: dict[str, any]):
        for k, v in data.items():
            if v == '':
                raise RequestData.error(data, REQUIRED, k)

    @staticmethod
    def require_save_game_as_is_not_reserved_name(data: dict[str, any]):
        if data.get(GAME_TO_LOAD) != NO_GAME_NAME_SELECTION:
            save_game_as = data.get(SAVE_GAME_AS, "")
            if save_game_as.lower() == NO_GAME_NAME_SELECTION.lower():
                raise RequestData.error(data, INVALID, SAVE_GAME_AS)

    @staticmethod
    def error(data: dict[str, any], message_key, candidate_key: str) -> ValidationError:
        lang_code = data.get(LANG_CODE, I18n.get_default_language_code())
        return ValidationError(f"{I18n.translate(lang_code, message_key)}: "
                               f"{I18n.translate(lang_code, candidate_key)}")

    @staticmethod
    def sync_to_session(data: dict[str, any]):
        RequestData._sync_to_session(data, GAME_SESSION)
        RequestData._sync_to_session(data, TRAINER)
        RequestData._sync_to_session(data, TIMEZONE)

    @staticmethod
    def _sync_to_session(data: dict[str, any], key: str):
        val = data.get(key)
        if val:
            session[key] = val
        else:
            data[key] = session.get(key)
