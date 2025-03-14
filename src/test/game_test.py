import unittest

from fastergerman.game import Game, Question, Score, Settings

questions = [
    {
        "verb": "warten",
        "answer": "auf",
        "example": "Ich warte ___ den Bus.",
        "translation": "I'm waiting for the bus.",
        "choices": ["mit", "für", "zu", "auf"],
        "level": "A1"
    },
    {
        "verb": "denken",
        "answer": "an",
        "example": "Ich denke ___ meine Familie.",
        "translation": "I'm thinking about my family.",
        "choices": ["über", "von", "an", "mit"],
        "level": "A2"
    },
    {
        "verb": "sich freuen",
        "answer": "auf",
        "example": "Ich freue mich ___ das Wochenende.",
        "translation": "I'm looking forward to the weekend.",
        "choices": ["für", "mit", "zu", "auf"],
        "level": "A2"
    }
]

class GameTestCase(unittest.TestCase):
    def test_question_removal_after_successive_correct_answer(self):
        """Test that a question is removed after being answered correctly {n} times."""
        max_consecutively_correct = 2
        num_questions = len(questions)
        game = Game("Test Game", Settings(30, 3, max_consecutively_correct, True, 0, num_questions),
                    [Question.of_dict(q) for q in questions],
                    Score(0, 0))

        for i in range(max_consecutively_correct):
            question = game.questions[0]
            game = game.on_question_answer(question, question.answer)

        exp_questions = num_questions - 1

        self.assertEqual(exp_questions, len(game.questions))


if __name__ == "__main__":
    unittest.main()
