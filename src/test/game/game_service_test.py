import unittest
from typing import List

from fastergerman.game import InMemoryGameStore, Question
from fastergerman.web import AbstractGameSessionProvider, GameService, SESSION_ID, ACTION


class TestGameSessionProvider(AbstractGameSessionProvider):
    def __init__(self, questions: dict[str, List[Question]]):
        self.__questions = questions

    def create_store(self, session_id: str, trainer: str):
        return InMemoryGameStore()

    def get_questions(self, trainer: str):
        return self.__questions.get(trainer, [])


class GameServiceTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verb_question = Question.of_dict({
            "answer": "warte",
            "example": "Ich ___ auf den Bus.",
            "translation": "I'm waiting for the bus.",
            "choices": ["warten", "warte", "wartest", "wartet"],
            "level": "A1"
        })
        self.preposition_question = Question.of_dict({
            "answer": "auf",
            "example": "Ich warte ___ den Bus.",
            "translation": "I'm waiting for the bus.",
            "choices": ["mit", "für", "zu", "auf"],
            "level": "A1"
        })
        self.questions = {
            "verb": [self.verb_question],
            "preposition": [self.preposition_question]
        }

    def game_session_provider_should_provide_questions_for_trainer(self, trainer):
        game_session_provider = TestGameSessionProvider(self.questions)
        game_session = game_session_provider.create_session("session-id", trainer)
        questions = game_session_provider.get_questions(trainer)
        for i in range(len(questions)):
            self.assertEqual(questions[i].example, game_session.get_game().questions[i].example)

    def test_game_session_provider_should_provide_questions_for_trainer(self):
        for trainer in self.questions.keys():
            self.game_session_provider_should_provide_questions_for_trainer(trainer)

    def game_service_should_provide_questions_for_trainer(self, trainer):
        game_session_provider = TestGameSessionProvider(self.questions)
        game_service = GameService(game_session_provider)
        game_service.trainers({ACTION: "update", SESSION_ID: "session-id", "trainer": trainer})
        game_session = game_service.get_session("session-id", trainer)
        questions = game_session_provider.get_questions(trainer)
        for i in range(len(questions)):
            self.assertEqual(questions[i].example, game_session.get_game().questions[i].example)

    def test_game_service_should_provide_questions_for_trainer(self):
        for trainer in self.questions.keys():
            self.game_service_should_provide_questions_for_trainer(trainer)

if __name__ == '__main__':
    unittest.main()
