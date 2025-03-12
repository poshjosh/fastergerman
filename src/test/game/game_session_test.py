import unittest
from typing import List
from unittest import mock

from fastergerman.game import GameFile, Question, GameSession, GameTimers, GameTimer


class GameSessionTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_dir = "fake/app/dir"
        self.game_to_load = "game1"

    def test_pending_game(self):
        with mock.patch.object(GameFile, "_require_data_dir") as mock_require_data_dir:
            mock_require_data_dir.return_value = f"{self.game_dir}/data"
            game_file = GameFile(self.game_dir)
            game_session = GameSession(game_file, self._given_questions(), self._given_timers())
            self.assertTrue(game_session.is_pending())
            self.assertIsNone(game_session.get_previous_question())
            self.assertIsNone(game_session.get_previous_answer())
            self.assertIsNone(game_session.get_current_question())
            self.assertIsNone(game_session.get_current_answer())

    def test_started_game(self):
        with mock.patch.object(GameFile, "_require_data_dir") as mock_require_data_dir, \
                mock.patch.object(GameSession, "get_game_to_load") as mock_get_game_to_load, \
                mock.patch.object(GameSession, "load_game"), \
                mock.patch.object(GameSession, "handle_question"):
            mock_get_game_to_load.return_value = self.game_to_load
            mock_require_data_dir.return_value = f"{self.game_dir}/data"
            game_file = GameFile(self.game_dir)
            game_session = GameSession(game_file, self._given_questions(), self._given_timers())
            game_session.start_game()
            self.assertTrue(game_session.is_running())
            self.assertIsNone(game_session.get_previous_question())
            self.assertIsNone(game_session.get_previous_answer())
            self.assertIsNotNone(game_session.get_current_question())
            self.assertIsNone(game_session.get_current_answer())

            self.assertTrue(game_session.get_countdown_timer().is_started())
            self.assertTrue(game_session.get_next_ques_timer().is_started())
            self.assertEqual(game_session.get_game_to_load(), self.game_to_load)

    def test_answered_question(self):
        with mock.patch.object(GameFile, "_require_data_dir") as mock_require_data_dir, \
                mock.patch.object(GameSession, "get_game_to_load") as mock_get_game_to_load, \
                mock.patch.object(GameSession, "load_game"), \
                mock.patch.object(GameSession, "handle_question"), \
                mock.patch.object(GameFile, "save_game"):
            mock_get_game_to_load.return_value = self.game_to_load
            mock_require_data_dir.return_value = f"{self.game_dir}/data"
            game_file = GameFile(self.game_dir)
            game_session = GameSession(game_file, self._given_questions(), self._given_timers())
            game_session.start_game()
            number_of_questions = game_session.get_max_questions()
            answer = "mit"
            game_session.handle_answer(answer)
            game_session.next_question()
            self.assertTrue(game_session.is_running())
            self.assertIsNotNone(game_session.get_previous_question())
            self.assertEqual(game_session.get_previous_answer(), answer)
            self.assertIsNotNone(game_session.get_current_question())
            self.assertIsNone(game_session.get_current_answer())
            self.assertEqual(number_of_questions, game_session.get_max_questions())

    @staticmethod
    def _given_timers() -> GameTimers:
        countdown_timer = GameTimer(1000)
        next_ques_timer = GameTimer(30000)
        class TestGameTimers(GameTimers):
            def get_countdown_timer(self) -> GameTimer:
                return countdown_timer
            def get_next_ques_timer(self) -> GameTimer:
                return next_ques_timer
        return TestGameTimers()

    @staticmethod
    def _given_questions() -> List[Question]:
        return [Question.of_dict({
                "verb": "warten",
                "preposition": "auf",
                "example": "Ich warte ___ den Bus.",
                "translation": "I'm waiting for the bus.",
                "choices": ["mit", "für", "zu", "auf"]
            }),
            Question.of_dict({
                "verb": "denken",
                "preposition": "an",
                "example": "Ich denke ___ meine Familie.",
                "translation": "I'm thinking about my family.",
                "choices": ["über", "von", "an", "mit"]
            })
        ]

if __name__ == '__main__':
    unittest.main()
