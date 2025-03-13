DEFAULT_LANGUAGE_CODE="en"

APP_SHORT_DESCRIPTION="app_short_description"
DISPLAY_QUESTION_TRANSLATION = "display_translation"
GAME_COMPLETED_MESSAGE = "game_completed_message"
GAME_TO_LOAD = "game_to_load"
INVALID = "invalid"
MAX_CONSECUTIVE_CORRECT_ANSWERS = "max_consecutively_correct"
MAX_NUMBER_OF_QUESTIONS = "max_number_of_questions"
NEW_GAME = "new_game"
NO_MORE_QUESTIONS = "no_more_questions"
NOT_FOUND = "not_found"
NUMBER_OF_CHOICES_PER_QUESTION = "number_of_choices"
PAUSE = "pause"
PLEASE_ENTER_NAME = "please_enter_name"
PREPOSITION_TRAINER = "preposition_trainer"
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
UNEXPECTED_ERROR = "unexpected_error"

config = {
    DEFAULT_LANGUAGE_CODE: {
        "display_name": "English",
        "dir": "ltr",
        "translations": {
            APP_SHORT_DESCRIPTION: "Learn german faster",
            DISPLAY_QUESTION_TRANSLATION: "Display question translation",
            GAME_COMPLETED_MESSAGE: "Game completed. You scored {} percent.",
            GAME_TO_LOAD: "Game to load",
            INVALID: "Not valid",
            MAX_CONSECUTIVE_CORRECT_ANSWERS: "Max consecutive correct answers",
            MAX_NUMBER_OF_QUESTIONS: "Max number of questions",
            NEW_GAME: "New game",
            NO_MORE_QUESTIONS: "No more questions available from total: {}, for range: {} to {}",
            NOT_FOUND: "Not found",
            NUMBER_OF_CHOICES_PER_QUESTION: "Number of choices per question",
            PAUSE: "Pause",
            PLEASE_ENTER_NAME: "Please enter a name",
            PREPOSITION_TRAINER: "Preposition Trainer",
            QUESTION_DISPLAY_TIME_SECONDS: "Question display time (seconds)",
            QUESTIONS_LEFT: "Questions left",
            REQUIRED: "Required",
            SAVE_GAME_AS: "Save game as",
            SCORE: "Score",
            SELECT_GAME_TO_LOAD: "Select game to load",
            SETTINGS: "Settings",
            START: "Start",
            START_AT_QUESTION_NUMBER: "Start at question number",
            START_GAME_PROMPT: "Click Start to begin",
            SUBMIT: "Submit",
            TIME: "Time",
            UNEXPECTED_ERROR: "Unexpected problem"
        }
    },
    "ar":{ "display_name": "العربية", "dir": "rtl" },
    "bn":{"display_name": "বাংলা"},
    "de":{
        "display_name": "Deutsch",
        "translations": {
            APP_SHORT_DESCRIPTION: "Schneller Deutsch lernen",
            DISPLAY_QUESTION_TRANSLATION: "Frageübersetzung anzeigen",
            GAME_COMPLETED_MESSAGE: "Spiel beendet. Du hast {} Prozent erreicht.",
            GAME_TO_LOAD: "Spiel zu laden",
            INVALID: "Nicht gültig",
            MAX_CONSECUTIVE_CORRECT_ANSWERS: "Max. aufeinanderfolgende richtige Antworten",
            MAX_NUMBER_OF_QUESTIONS: "Maximale Anzahl von Fragen",
            NEW_GAME: "Neues Spiel",
            NO_MORE_QUESTIONS: "Keine weiter Fragen verfügbar von insgesamt: {}, für Bereich: {} bis {}",
            NOT_FOUND: "Nicht gefunden",
            NUMBER_OF_CHOICES_PER_QUESTION: "Anzahl der Auswahlmöglichkeiten pro Frage",
            PAUSE: "Pause",
            PLEASE_ENTER_NAME: "Bitte geben Sie einen Namen ein",
            PREPOSITION_TRAINER: "Präpositionstrainer",
            QUESTION_DISPLAY_TIME_SECONDS: "Frage-Anzeigezeit (Sekunden)",
            QUESTIONS_LEFT: "Verbleibende Fragen",
            REQUIRED: "Erforderlich",
            SAVE_GAME_AS: "Spiel speichern unter",
            SCORE: "Punktestand",
            SELECT_GAME_TO_LOAD: "Spiel zum Laden auswählen",
            SETTINGS: "Einstellungen",
            START: "Start",
            START_AT_QUESTION_NUMBER: "Start bei Fragenummer",
            START_GAME_PROMPT: "Klicken Sie auf Start, um zu beginnen",
            SUBMIT: "Abschicken",
            TIME: "Zeit",
            UNEXPECTED_ERROR: "Unerwartetes Problem"
        }
     },
    "es":{"display_name": "Español"},
    "fr":{"display_name": "Français"},
    "hi":{"display_name": "हिन्दी"},
    "it":{"display_name": "Italiano"},
    "ja":{"display_name": "日本語"},
    "ko":{"display_name": "한국어"},
    "ru":{"display_name": "Русский"},
    "tr":{"display_name": "Türkçe"},
    "uk":{"display_name": "українська"},
    "zh":{"display_name": "中文"}
}
    

class I18n:
    @staticmethod
    def is_supported(lang_code: str):
        return I18n.get_config(lang_code).get("translations", None) is not None

    @staticmethod
    def get_supported_language_codes():
        return [e for e in config.keys() if I18n.is_supported(e) is True]

    @staticmethod
    def get_supported_languages():
        supported_languages = []
        for k in I18n.get_supported_language_codes():
            v = config[k]
            supported_languages.append({"code": k, "display_name": v["display_name"]})
        return supported_languages

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
        elif lang != DEFAULT_LANGUAGE_CODE:
            val = I18n.translate(DEFAULT_LANGUAGE_CODE, key, *args)
            return val if val else key
        else:
            raise ValueError(f"{lang} translation not found for key {key}")

    @staticmethod
    def get_dir(lang) -> str:
        return I18n.get_config(lang).get("dir", "ltr")

    @staticmethod
    def get_translations(lang) -> dict[str, str]:
        translation_keys = I18n.get_config(DEFAULT_LANGUAGE_CODE)["translations"].keys()
        result = {}
        for k in translation_keys:
            result[k] = I18n.translate(lang, k)
        return result

