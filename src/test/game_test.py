import unittest

from fastergerman.game import Game, Question, Score, Settings

DEFAULT_QUESTIONS = [
    {
        "verb": "warten",
        "preposition": "auf",
        "example": "Ich warte ___ den Bus.",
        "translation": "I'm waiting for the bus.",
        "choices": ["mit", "für", "zu", "auf"]
    },
    {
        "verb": "denken",
        "preposition": "an",
        "example": "Ich denke ___ meine Familie.",
        "translation": "I'm thinking about my family.",
        "choices": ["über", "von", "an", "mit"]
    },
    {
        "verb": "sich freuen",
        "preposition": "auf",
        "example": "Ich freue mich ___ das Wochenende.",
        "translation": "I'm looking forward to the weekend.",
        "choices": ["für", "mit", "zu", "auf"]
    }
]

class GameTestCase(unittest.TestCase):
    def test_question_removal_after_successive_correct_answer(self):
        """Test that a question is removed after being answered correctly {n} times."""
    max_consecutively_correct = 2
    num_questions = len(DEFAULT_QUESTIONS)
    game = Game("Test Game", Settings(30, 3, max_consecutively_correct, True, 0, num_questions),
                [Question.of_dict(q) for q in DEFAULT_QUESTIONS],
                Score(0, 0))

    for i in range(max_consecutively_correct):
        question = game.questions[0]
        game = game.on_question_answer(question, question.preposition)

    exp_questions = num_questions - 1

    if len(game.questions) != exp_questions:
        raise ValueError(f"Error: expected {exp_questions} questions, "
                         f"but found {len(game.questions)}")


if __name__ == "__main__":
    unittest.main()
