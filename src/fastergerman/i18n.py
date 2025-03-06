DEFAULT_LANGUAGE_CODE="en"
supported_language_code_to_display_name = {
    "ar":"العربية",
    "bn":"বাংলা",
    "de":"Deutsch",
    "en":"English",
    "es":"Español",
    "fr":"Français",
    "hi":"हिन्दी",
    "it":"Italiano",
    "ja":"日本語",
    "ko":"한국어",
    "ru":"Русский",
    "tr":"Türkçe",
    "uk":"українська",
    "zh":"中文"
}

INVALID = "invalid"
PLEASE_ENTER_NAME = "please_enter_name"
SETTINGS = "settings"
GAME_TO_LOAD = "game_to_load"
SAVE_GAME_AS = "save_game_as"
QUESTION_DISPLAY_TIME_SECONDS = "question_display_time"
REQUIRED = "required"
NUMBER_OF_CHOICES_PER_QUESTION = "number_of_choices"
MAX_CONSECUTIVE_CORRECT_ANSWERS = "max_consecutively_correct"
DISPLAY_QUESTION_TRANSLATION = "display_translation"
START_AT_QUESTION_NUMBER = "start_at_question_number"
MAX_NUMBER_OF_QUESTIONS = "max_number_of_questions"
SELECT_GAME_TO_LOAD = "select_game_to_load"
START_GAME_PROMPT = "start_game_prompt"
QUESTIONS_LEFT = "questions_left"
START = "start"
PAUSE = "pause"
SCORE = "score"
SUBMIT = "submit"
TIME = "time"
GAME_COMPLETED_MESSAGE = "Game completed. You scored {0} percent."

config = {
    "en": {
        "dir": "ltr",
        "display_name": "English",
        "translations": {
            INVALID: "Not valid",
            PLEASE_ENTER_NAME: "Please enter a name",
            SETTINGS: "Settings",
            GAME_TO_LOAD: "Game to load",
            SAVE_GAME_AS: "Save game as",
            QUESTION_DISPLAY_TIME_SECONDS: "Question display time (seconds)",
            REQUIRED: "Required",
            NUMBER_OF_CHOICES_PER_QUESTION: "Number of choices per question",
            MAX_CONSECUTIVE_CORRECT_ANSWERS: "Max consecutive correct answers",
            DISPLAY_QUESTION_TRANSLATION: "Display question translation",
            START_AT_QUESTION_NUMBER: "Start at question number",
            MAX_NUMBER_OF_QUESTIONS: "Max number of questions",
            SELECT_GAME_TO_LOAD: "Select game to load",
            START_GAME_PROMPT: "Click Start to begin",
            QUESTIONS_LEFT: "Questions left",
            START: "Start",
            PAUSE: "Pause",
            SCORE: "Score",
            SUBMIT: "Submit",
            TIME: "Time",
            GAME_COMPLETED_MESSAGE: "Game completed. You scored {} percent."
        }
    }
}
    

class I18n:
    @staticmethod
    def get_supported_languages():
        supported_languages = []
        codes: [str] = [str(k) for k,v in supported_language_code_to_display_name.items()]
        for code in codes:
            if not code:
                continue
            lang = {"code":code, "display_name":supported_language_code_to_display_name.get(code, code)}
            supported_languages.append(lang)
        return supported_languages

    @staticmethod
    def get_supported_language_codes():
        return [e["code"] for e in I18n.get_supported_languages()]

    @staticmethod
    def get_config(lang: str) -> dict[str, any]:
        lang = str(lang).lower()
        found = config.get(lang, None)
        if found:
            return found
        parts = lang.split('-')
        lang = parts[0] if len(parts) > 1 else DEFAULT_LANGUAGE_CODE
        return config.get(lang, {})

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
        else:
            return key

    @staticmethod
    def get_dir(lang) -> str:
        return I18n.get_config(lang).get("dir", "ltr")

    @staticmethod
    def get_translations(lang) -> str:
        return I18n.get_config(lang)["translations"]
