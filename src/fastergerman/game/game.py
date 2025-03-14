from dataclasses import dataclass, asdict
from random import shuffle
from typing import List

class LanguageLevel:
    VALUES = ["A1", "A2", "B1", "B2", "C1", "C2"]
    @staticmethod
    def ordinal(level: str) -> int:
        return LanguageLevel.VALUES.index(level)

    @staticmethod
    def is_lte(a: str, b: str) -> bool:
        return LanguageLevel.ordinal(a) <= LanguageLevel.ordinal(b)

@dataclass(frozen=True)
class Score:
    success: int = 0
    total: int = 0

    @staticmethod
    def of_dict(score_dict: dict) -> 'Score':
        return Score(score_dict.get("success", 0), score_dict.get("total", 0))

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

    def advance(self, correct: bool) -> 'Score':
        return Score(self.success + 1 if correct else self.success, self.total + 1)

    def to_percent(self) -> float:
        return 0 if self.success == 0 else (self.success / self.total) * 100

    def __str__(self):
        return f"{self.success}/{self.total}"

class NoMoreQuestionsError(Exception):
    def __init__(self, total, start, end, *args):
        super().__init__(total, start, end, *args)
        self.total = total
        self.start = start
        self.end = end

@dataclass(frozen=True)
class Question:
    answer: str
    example: str
    translation: str
    choices: list[str]
    level: str
    consecutively_correct: int = 0

    @staticmethod
    def of_dict(question_dict: dict) -> 'Question':
        answer = question_dict["answer"]
        choices = question_dict["choices"]
        if answer not in choices:
            choices.append(answer)
        shuffle(choices)
        return Question(answer,
                        question_dict["example"],
                        question_dict["translation"],
                        choices,
                        question_dict["level"],
                        int(question_dict.get("consecutively_correct", 0)))

    def to_dict(self) -> dict[str, any]:
        return asdict(self)

    def with_number_of_choices(self, number_of_choices: int) -> 'Question':
        if number_of_choices >= len(self.choices):
            return self
        choices = [self.answer]
        for i in range(number_of_choices - 1):
            if self.choices[i] == self.answer:
                continue
            choices.append(self.choices[i])
        shuffle(choices)
        return Question(self.answer, self.example, self.translation,
                        choices, self.level, self.consecutively_correct)

    def on_answer(self, answer: str) -> 'Question':
        return Question(self.answer, self.example, self.translation,
                        self.choices, self.level,
                        self.consecutively_correct + 1 if self.is_answer(answer) else 0)

    def is_answer(self, answer: str) -> bool:
        return answer == self.answer


@dataclass(frozen=True)
class Settings:
    question_display_time: int = 30
    number_of_choices: int = 3
    max_consecutively_correct: int = 2
    display_translation: bool = True
    start_at_question_number: int = 0
    max_number_of_questions: int = 20
    language_level: str = "A2"

    @staticmethod
    def of_dict(settings_dict: dict) -> 'Settings':
        dt = settings_dict.get("display_translation", True)
        return Settings(
            int(settings_dict.get("question_display_time", 30)),
            int(settings_dict.get("number_of_choices", 3)),
            int(settings_dict.get("max_consecutively_correct", 2)),
            dt.lower() == "true" if isinstance(dt, str) else bool(dt),
            int(settings_dict.get("start_at_question_number", 0)),
            int(settings_dict.get("max_number_of_questions", 20)),
            settings_dict.get("language_level", "A2"))

    def to_dict(self) -> dict[str, any]:
        return asdict(self)

    def get_questions_from(self, questions: List[Question]) -> List[Question]:
        questions = [q for q in questions if LanguageLevel.is_lte(q.level, self.language_level)]
        questions.sort(key=lambda q: LanguageLevel.ordinal(q.level))
        first_question = self.start_at_question_number
        max_questions = self.max_number_of_questions
        number_of_ques = len(questions)
        last_question = first_question + max_questions
        if last_question > number_of_ques:
            last_question = number_of_ques
        result = questions[first_question:last_question]
        if len(result) == 0:
            raise NoMoreQuestionsError(number_of_ques, first_question, last_question)
        return [q.with_number_of_choices(self.number_of_choices) for q in result]

    def with_value(self, key: str, value: any) -> 'Settings':
        settings_dict = self.to_dict()
        if key not in settings_dict:
            raise ValueError(f"Invalid key {key}")
        existing = settings_dict.get(key)
        if existing == value:
            return self
        settings_dict[key] = value
        return Settings.of_dict(settings_dict)

    def next(self) -> 'Settings':
        return Settings(
            self.question_display_time,
            self.number_of_choices,
            self.max_consecutively_correct,
            self.display_translation,
            self.start_at_question_number + self.max_number_of_questions,
            self.max_number_of_questions)

@dataclass(frozen=True)
class Game:
    name: str
    settings: Settings
    questions: list[Question]
    score: Score = Score(0, 0)

    @staticmethod
    def of_dict(game_dict: dict) -> 'Game':
        Settings.of_dict(game_dict["settings"])
        return Game(game_dict["name"],
                    Settings.of_dict(game_dict["settings"]),
                    [Question.of_dict(q) for q in game_dict["questions"]],
                    Score.of_dict(game_dict["score"]))

    def to_dict(self) -> dict[str, any]:
        return {
            "name": self.name,
            "settings": self.settings.to_dict(),
            "questions": [q.to_dict() for q in self.questions],
            "score": self.score.to_dict()
        }

    def on_question_answer(self, question: Question, answer: str) -> 'Game':
        updated_question = question.on_answer(answer)
        questions = [q for q in self.questions]
        if updated_question.consecutively_correct >= self.settings.max_consecutively_correct:
            # Return the game without the question
            questions.remove(question)
        else:
            index = questions.index(question)
            questions.remove(question)
            questions.insert(index, updated_question)
        return Game(self.name,
                    self.settings,
                    questions,
                    self.score.advance(question.is_answer(answer)))

    def with_name(self, name: str) -> 'Game':
        if self.name == name:
            return self
        return Game(
            name,
            self.settings,
            self.questions,
            self.score)

    def __str__(self):
        data = self.to_dict()
        data["questions"] = len(self.questions)
        return str(data)