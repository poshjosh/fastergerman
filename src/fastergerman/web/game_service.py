import logging

from fastergerman.game import GameSession, SimpleGameTimer, Settings, Question, GameTimer
from fastergerman.web import SESSION_ID, ACTION

logger = logging.getLogger(__name__)


class WebGameSession(GameSession):
    def __init__(self):
        super().__init__()
        self.__countdown_timer = SimpleGameTimer(1000)
        self.__next_ques_timer = None

    def handle_question(self, question: Question):
        """Subclasses should implement this method to process the Question."""
        logger.debug(f"Please implement handling questions. Question: {question}")

    def get_countdown_timer(self) -> GameTimer:
        return self.__countdown_timer

    def get_next_ques_timer(self) -> GameTimer:
        if self.__next_ques_timer is None:
            logger.debug(f"Creating next question timer. Question display time millis: "
                         f"{self._get_question_display_time_millis()}")
            # TODO - This timer should change, anytime game settings.question_display_time changes
            self.__next_ques_timer = SimpleGameTimer(self._get_question_display_time_millis())
        return self.__next_ques_timer

    def _get_question_display_time_millis(self) -> int:
        return self.get_game().settings.question_display_time * 1000

class GameService:
    def __init__(self):
        self.__game_sessions = dict[str, GameSession]()

    def close(self):
        for session in self.__game_sessions.values():
            session.close()
        self.__game_sessions.clear()

    def get_or_create_session(self, config: dict[str, any]) -> GameSession:
        session_id = config[SESSION_ID]
        if session_id not in self.__game_sessions.keys():
            self.__game_sessions[session_id] = WebGameSession()
        return self.__game_sessions[session_id]

    def preposition_trainer(self, config: dict[str, any]) -> GameSession:

        game_session: GameSession = self.get_or_create_session(config)

        if "game_to_load" in config:
            game_to_load = config["game_to_load"]
            game_session.set_game_to_load(game_to_load)
            game_session.load_game(game_to_load, Settings.of_dict(config))
            save_game_as = config.get("save_game_as", game_to_load)
        else:
            save_game_as = config.get("save_game_as", None)

        if save_game_as:
            game_session.save_game_as(save_game_as)


        action = config.get(ACTION, None)
        if action == "start":
            game_session.start_game()
        elif action == "pause":
            game_session.pause_game()
        elif action == "next":
            game_session.next_question(True)
        elif action == "answer":
            game_session.handle_answer(config.get("answer", ""))

        return game_session
