import unittest
from typing import List

from fastergerman.game import Question, GameSession, GameTimers, GameTimer, Score, InMemoryGameStore


class GameSessionTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_to_load = "game1"

    def test_pending_game(self):
        print("test_pending_game")
        game_session = self._given_game_session()
        self.assertTrue(game_session.is_pending())
        self.assertIsNone(game_session.get_previous_question())
        self.assertIsNone(game_session.get_previous_answer())
        self.assertIsNone(game_session.get_current_question())
        self.assertIsNone(game_session.get_current_answer())

    def test_started_game(self):
        print("test_started_game")
        game_session = self._given_game_session()
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
        print("test_answered_question")
        game_session = self._given_game_session()
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
        self.assertNotEqual(Score(0, 0), game_session.get_game().score)

    def test_pause_then_resume_does_not_change_score(self):
        print("test_pause_then_resume_does_not_change_score")
        game_session = self._given_game_session()
        game_session.start_game()
        game_session.get_max_questions()
        game_session.handle_answer("mit")
        game_session.next_question()
        self.assertTrue(game_session.is_running())
        score = game_session.get_game().score

        game_session.pause_game()
        self.assertTrue(game_session.is_paused())
        self.assertEqual(score, game_session.get_game().score)
        game_session.start_game()
        self.assertTrue(game_session.is_running())
        self.assertEqual(score, game_session.get_game().score)

    def _given_game_session(self) -> GameSession:
        game_store = InMemoryGameStore(self.game_to_load)
        return GameSession(game_store, self._given_questions(), self._given_timers())

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
