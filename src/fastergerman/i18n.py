import json
import logging
import os

logger = logging.getLogger(__name__)

APP_SHORT_DESCRIPTION="app_short_description"
ASK_ANYTHING = "ask_anything"
CHAT="chat"
CHAT_DISABLED="chat_disabled"
CHAT_MODEL = "chat_model"
CHAT_MODEL_API_KEY = "chat_model_api_key"
DISPLAY_QUESTION_TRANSLATION = "display_translation"
GAME_COMPLETED_MESSAGE = "game_completed_message"
GAME_TO_LOAD = "game_to_load"
# GERMAN = "german" TODO remove from translation files
INVALID = "invalid"
LANGUAGE_LEVEL = "language_level"
MAX_CONSECUTIVE_CORRECT_ANSWERS = "max_consecutively_correct"
MAX_NUMBER_OF_QUESTIONS = "max_number_of_questions"
LLM_NOT_FOUND = "llm_not_found"
NEW_GAME = "new_game"
NO_MORE_QUESTIONS = "no_more_questions"
NOT_FOUND = "not_found"
NUMBER_OF_CHOICES_PER_QUESTION = "number_of_choices"
PAUSE = "pause"
PLEASE_ENTER_NAME = "please_enter_name"
PREPOSITION_TRAINER = "preposition_trainer"
PROVIDE_CHAT_MODEL_API_KEY = "provide_chat_model_api_key"
QUESTION_DISPLAY_TIME_SECONDS = "question_display_time"
QUESTIONS_LEFT = "questions_left"
REQUIRED = "required"
SAVE_GAME_AS = "save_game_as"
SCORE = "score"
SELECT_GAME_TO_LOAD = "select_game_to_load"
SETTINGS = "settings"
START = "start"
START_AT_QUESTION_NUMBER = "start_at_question_number"
START_GAME_PROMPT = "start_game_prompt"
SUBMIT = "submit"
TIME = "time"
TOO_MANY_REQUESTS = "too_many_requests"
TYPE_HERE = "type_here"
UNEXPECTED_ERROR = "unexpected_error"
VERB_TRAINER = "verb_trainer"

class I18n:
    __default_lang_code = "en"
    __config = {}

    @staticmethod
    def init(default_lang_code: str = "en", directory: str = "resources/config/i18n"):
        logger.debug(f"Default language code: {default_lang_code}, loading translations from: {directory}")
        def read_json(file_path):
            with open(file_path, 'r+') as openfile:
                return json.load(openfile)

        entries = os.listdir(directory)
        for entry in entries:
            if entry.lower().endswith(".json") is False:
                continue
            path = os.path.join(directory, entry)
            if os.path.isfile(path) is False:
                continue
            lang_code, _ = os.path.splitext(entry)
            I18n.__config[lang_code] = read_json(path)
            logger.debug(f"Loaded translations for {lang_code}")

        code = default_lang_code.split('-')[0]
        if code not in I18n.__config:
            raise ValueError(f"Translations for default language '{code}' not found")
        I18n.__default_lang_code = code

    @staticmethod
    def get_english_name_for_code(lang_code: str) -> str:
        return I18n.get_config(lang_code).get("english_name", lang_code)

    @staticmethod
    def get_code_for_english_name(english_name: str) -> str:
        return I18n.__default_lang_code

    @staticmethod
    def is_supported(lang_code: str):
        return I18n.get_config(lang_code).get("translations", None) is not None

    @staticmethod
    def get_default_language_code():
        return I18n.__default_lang_code

    @staticmethod
    def get_supported_language_codes():
        return [e for e in I18n.__config.keys() if I18n.is_supported(e) is True]

    @staticmethod
    def get_supported_languages():
        supported_languages = []
        for k in I18n.get_supported_language_codes():
            v = I18n.__config[k]
            supported_languages.append({"code": k, "display_name": v["display_name"]})
        return supported_languages

    @staticmethod
    def get_config(lang: str) -> dict[str, any]:
        lang = str(lang).lower()
        found = I18n.__config.get(lang, None)
        if found:
            return found
        parts = lang.split('-')
        lang = parts[0] if len(parts) > 1 else I18n.get_default_language_code()
        return I18n.__config.get(lang, {})

    @staticmethod
    def translate_default(key: str, *args) -> str:
        return I18n.translate(I18n.get_default_language_code(), key, *args)

    @staticmethod
    def translate(lang: str, key: str, *args) -> str:
        """
        Translate a key to a language.
        If language code has a sub part e.g. zh-CN fallback to zh, otherwise fallback to DEFAULT_LANG
        :param lang: The language code to translate to.
        :param key: The key to translate.
        :return: The translated string.
        """
        val = I18n.get_config(lang).get("translations", {}).get(key, None)
        if val:
            return str(val).format(*args) if args else val
        elif lang != I18n.get_default_language_code():
            val = I18n.translate_default(key, *args)
            return val if val else key
        else:
            raise ValueError(f"{lang} translation not found for key {key}")

    @staticmethod
    def get_display_name(lang_code: str, default: str) -> str:
        return I18n.get_config(lang_code).get("display_name", default)

    @staticmethod
    def get_dir(lang) -> str:
        return I18n.get_config(lang).get("dir", "ltr")

    @staticmethod
    def get_translations(lang) -> dict[str, str]:
        translation_keys = I18n.get_config(I18n.get_default_language_code())["translations"].keys()
        result = {}
        for k in translation_keys:
            result[k] = I18n.translate(lang, k)
        return result

