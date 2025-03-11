import unittest
from unittest import mock

from fastergerman.game import FileQuestionsSource


class QuestionsTestCase(unittest.TestCase):
    def test_questions_loading(self):
        questions_type = "preposition"
        questions_json = {
            "type": questions_type,
            "description": "German verbs and their prepositions",
            "questions": [
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
                }
            ]
        }
        with mock.patch.object(FileQuestionsSource, "_load_questions") as mock_load_questions, \
            mock.patch.object(FileQuestionsSource, "_to_paths") as mock_to_paths:
            mock_load_questions.return_value = questions_type, questions_json
            path = "fake_path"
            mock_to_paths.return_value = [path]
            source = FileQuestionsSource(path)
            questions = source.load_questions().get(questions_type)
            self.assertEqual(len(questions_json["questions"]), len(questions))

    def test_questions_loading_when_no_questions(self):
        questions_type = "preposition"
        questions_json = {}
        with mock.patch.object(FileQuestionsSource, "_load_questions") as mock_load_questions, \
                mock.patch.object(FileQuestionsSource, "_to_paths") as mock_to_paths:
            mock_load_questions.return_value = questions_type, questions_json
            path = "fake_path"
            mock_to_paths.return_value = [path]
            source = FileQuestionsSource(path)
            self.assertRaises(ValueError, source.load_questions)

if __name__ == '__main__':
    unittest.main()
