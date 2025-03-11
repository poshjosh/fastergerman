from abc import abstractmethod, ABC
from typing import List

from fastergerman.file import read_json
from fastergerman.game import Question

class QuestionsSource(ABC):
    @abstractmethod
    def get_questions(self) -> List[Question]:
        raise NotImplementedError("get_questions() must be implemented.")

class FileQuestionsSource(QuestionsSource):
    def __init__(self, source: str):
        self.__source = source

    def get_questions(self) -> List[Question]:
        json_dict = read_json(self.__source)
        if not json_dict or len(json_dict) < 1:
            raise ValueError("No questions found.")
        questions = json_dict["questions"]
        return [Question.of_dict(q) for q in questions if q.get("priority") != "low"]