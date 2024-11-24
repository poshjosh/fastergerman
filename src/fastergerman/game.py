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

    def __str__(self):
        return f"{self.success}/{self.total}"


@dataclass(frozen=True)
class Game:
    name: str
    questions: list[dict]
    score: Score

    def advance_score(self, correct: bool) -> 'Game':
        return Game(
            self.name,
            self.questions,
            self.score.advance(correct))

    def with_name(self, name: str) -> 'Game':
        return Game(
            name,
            self.questions,
            self.score)

    def with_questions(self, questions: list[dict]) -> 'Game':
        return Game(
            self.name,
            questions,
            self.score)
