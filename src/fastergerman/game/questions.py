import os.path
from abc import abstractmethod, ABC
from typing import List

from fastergerman.file import read_json
from fastergerman.game import Question


class QuestionsSource(ABC):
    @abstractmethod
    def load_questions(self) -> dict[str, List[Question]]:
        raise NotImplementedError("load_questions() must be implemented.")

class FileQuestionsSource(QuestionsSource):
    def __init__(self, source: str):
        self.__paths = FileQuestionsSource._to_paths(source)
        if not self.__paths:
            raise ValueError(f"Not a valid questions source: {source}")

    def load_questions(self) -> dict[str, List[Question]]:
        result = {}
        for path in self.__paths:
            ques_type, json = self._load_questions(path)
            if not json:
                continue
            questions = json["questions"]
            print(f"{__name__} Found {len(questions)} questions of type: {ques_type} from: {path}")
            result[ques_type] = [Question.of_dict(q) for q in questions]
            print(f"{__name__} Loaded {len(result[ques_type])} questions of type: {ques_type} from: {path}")
        if not result:
            raise ValueError(f"No questions found for: {self.__paths}")
        return result

    @staticmethod
    def _to_paths(source) -> [str]:
        if os.path.isfile(source) is True:
            return [source] if os.path.exists(source) is True else []
        paths = []
        if os.path.exists(source) is False:
            return paths
        for name in os.listdir(source):
            path = os.path.join(source, name)
            if os.path.isfile(path) and os.path.exists(path) is True:
                paths.append(path)
        return paths

    @staticmethod
    def _load_questions(filepath: str):
        json = read_json(filepath)
        ques_type = FileQuestionsSource._require_type(filepath, json)
        return ques_type, json

    @staticmethod
    def _require_type(path: str, json):
        name, _ = os.path.splitext(path)
        ques_type = json.get("type", name)
        if not ques_type:
            raise ValueError(f"Could not determine type, for questions at: {path}")
        return ques_type

