from dataclasses import dataclass, asdict

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


@dataclass(frozen=True)
class Settings:
    question_display_time: int = 30
    number_of_choices: int = 3
    max_consecutively_correct: int = 2
    display_translation: bool = True
    start_at_question_number: int = 0
    max_number_of_questions: int = 20

    @staticmethod
    def of_dict(settings_dict: dict) -> 'Settings':
        return Settings(
            int(settings_dict.get("question_display_time", 30)),
            int(settings_dict.get("number_of_choices", 3)),
            int(settings_dict.get("max_consecutively_correct", 2)),
            bool(settings_dict.get("display_translation", True)),
            int(settings_dict.get("start_at_question_number", 0)),
            int(settings_dict.get("max_number_of_questions", 20)))

    def to_dict(self) -> dict[str, any]:
        return asdict(self)

    def with_value(self, key: str, value: any) -> 'Settings':
        settings_dict = self.to_dict()
        if key not in settings_dict:
            raise ValueError(f"Invalid key {key}")
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
class Question:
    verb: str
    preposition: str
    example: str
    translation: str
    choices: list[str]
    priority: str = "medium"
    consecutively_correct: int = 0

    @staticmethod
    def of_dict(question_dict: dict) -> 'Question':
        return Question(question_dict["verb"],
                        question_dict["preposition"],
                        question_dict["example"],
                        question_dict["translation"],
                        question_dict["choices"],
                        question_dict.get("priority", "medium"),
                        int(question_dict.get("consecutively_correct", 0)))

    def to_dict(self) -> dict[str, any]:
        return asdict(self)

    def on_answer(self, answer: str) -> 'Question':
        return Question(self.verb, self.preposition, self.example, self.translation,
                        self.choices, self.priority,
                        self.consecutively_correct + 1 if self.is_answer(answer) else 0)

    def is_answer(self, answer: str) -> bool:
        return answer == self.preposition


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
            # Did not work
#            questions = [q for q in self.questions if q.verb != question.verb]
        else:
            index = questions.index(question)
            questions.remove(question)
            questions.insert(index, updated_question)
            # Did not work
#            questions = [updated_question if q.verb == question.verb else q for q in self.questions]
        return Game(self.name,
                    self.settings,
                    questions,
                    self.score.advance(question.is_answer(answer)))

    def with_name(self, name: str) -> 'Game':
        return Game(
            name,
            self.settings,
            self.questions,
            self.score)

    def with_settings(self, settings: Settings) -> 'Game':
        return Game(
            self.name,
            settings,
            self.questions,
            self.score)
