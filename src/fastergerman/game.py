from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    success: int
    total: int

    @staticmethod
    def of_dict(score_dict: dict) -> 'Score':
        return Score(score_dict.get("success", 0), score_dict.get("total", 0))

    def advance(self, correct: bool) -> 'Score':
        return Score(self.success + 1 if correct else self.success, self.total + 1)

    def to_percent(self) -> float:
        return (self.success / self.total) * 100

    def __str__(self):
        return f"{self.success}/{self.total}"


@dataclass(frozen=True)
class Settings:
    question_display_time: int
    number_of_choices: int
    max_consecutively_correct: int
    display_translation: bool

    @staticmethod
    def of_dict(settings_dict: dict) -> 'Settings':
        return Settings(
            settings_dict.get("question_display_time", 30),
            settings_dict.get("number_of_choices", 3),
            settings_dict.get("max_consecutively_correct", 2),
            settings_dict.get("display_translation", True))


@dataclass(frozen=True)
class Question:
    verb: str
    preposition: str
    example: str
    translation: str
    choices: list[str]
    priority: str
    consecutively_correct: int

    @staticmethod
    def of_dict(question_dict: dict) -> 'Question':
        return Question(question_dict["verb"],
                        question_dict["preposition"],
                        question_dict["example"],
                        question_dict["translation"],
                        question_dict["choices"],
                        question_dict.get("priority", "medium"),
                        question_dict.get("consecutively_correct", 0))

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
    score: Score

    @staticmethod
    def of_dict(game_dict: dict) -> 'Game':
        Settings.of_dict(game_dict["settings"])
        return Game(game_dict["name"],
                    Settings.of_dict(game_dict["settings"]),
                    [Question.of_dict(q) for q in game_dict["questions"]],
                    Score.of_dict(game_dict["score"]))

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

    def with_questions(self, questions: list[Question]) -> 'Game':
        return Game(
            self.name,
            self.settings,
            questions,
            self.score)
