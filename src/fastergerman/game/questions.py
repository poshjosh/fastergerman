import os
from typing import List

from fastergerman.file import read_json
from fastergerman.game import Question

class QuestionsLoader:
    @staticmethod
    def load_questions(source: str) -> List[Question]:
        json_dict = read_json(source)
        if not json_dict or len(json_dict) < 1:
            raise ValueError("No questions found.")
        questions = json_dict["questions"]
        return [Question.of_dict(q) for q in questions if q.get("priority") != "low"]