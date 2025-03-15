import unittest

from fastergerman.game import Game, Question, Settings, LanguageLevel


class GameTestCase(unittest.TestCase):
    def questions_should_have_correct_number_of_choices(self, number_of_choices: int):
        questions_json = [
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
                "choices": ["über", "von", "an", "mit", "für", "zu"],
                "level": "A2"
            }
        ]

        settings = Settings.of_dict({"number_of_choices": number_of_choices})
        questions = settings.get_questions_from([Question.of_dict(q) for q in questions_json])
        game = Game("test-game", settings, questions)

        self.assertEqual(number_of_choices, game.settings.number_of_choices)
        for question in game.questions:
            self.assertEqual(number_of_choices, len(question.choices))

    test_questions_should_have_2_choices = lambda self: self.questions_should_have_correct_number_of_choices(2)
    test_questions_should_have_3_choices = lambda self: self.questions_should_have_correct_number_of_choices(3)
    test_questions_should_have_4_choices = lambda self: self.questions_should_have_correct_number_of_choices(4)

    def should_have_questions_of_level_and_below(self, language_level: str):
        questions_json = [
            {
                "verb": "warten",
                "answer": "auf",
                "example": "Ich warte ___ den Bus.",
                "translation": "I'm waiting for the bus.",
                "choices": ["mit", "für", "zu", "auf"],
                "level": language_level
            },
            {
                "verb": "denken",
                "answer": "an",
                "example": "Ich denke ___ meine Familie.",
                "translation": "I'm thinking about my family.",
                "choices": ["über", "von", "an", "mit", "für", "zu"],
                "level": LanguageLevel.next(language_level, language_level)
            }
        ]

        settings = Settings.of_dict({"language_level": language_level})
        questions = settings.get_questions_from([Question.of_dict(q) for q in questions_json])
        game = Game("test-game", settings, questions)

        self.assertEqual(language_level, game.settings.language_level)
        for question in game.questions:
            self.assertTrue(LanguageLevel.is_lte(question.level, language_level))

    def test_questions_should_have_correct_level(self):
        for level in LanguageLevel.VALUES:
            self.should_have_questions_of_level_and_below(level)


if __name__ == '__main__':
    unittest.main()
