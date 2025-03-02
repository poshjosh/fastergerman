import logging
import uuid
from typing import Union

from fastergerman.i18n import I18n

logger = logging.getLogger(__name__)

LANG_CODE = "lang_code"
SESSION_ID = "session_id"
ACTION = "action"


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
    def preposition_trainer_config(request, validate: bool = True) -> dict[str, any]:

        request_data = {**dict(request.form), **dict(request.args)}

        try:
            request_data = RequestData.strip_values(request_data)
            logger.debug(f"Input form data: {request_data}")

            request_data[LANG_CODE] = RequestData.get_language_code(request)
            request_data[SESSION_ID] = RequestData.get(request, SESSION_ID, str(uuid.uuid4().hex))

            if validate is True:
                RequestData.validate_form_data(request_data)

            logger.debug(f"Output request data: {request_data}")
            return request_data
        except ValueError as value_ex:
            logger.exception(value_ex)
            raise ValidationError(value_ex.args[0])

    @staticmethod
    def get_language_code(request) -> str or None:
        supported_lang_codes = I18n.get_supported_language_codes()
        return request.accept_languages.best_match(supported_lang_codes)

    @staticmethod
    def strip_values(data: dict[str, any]):
        for k, v in data.items():
            v = v.strip() if isinstance(v, str) else v
            data[k] = v
        return data

    @staticmethod
    def validate_form_data(form_data: dict[str, any]):
        for k, v in form_data.items():
            if v == '':
                raise ValidationError(f"'{k}' is required")
