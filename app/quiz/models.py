from dataclasses import dataclass
from typing import Optional

from app.store.database.gino import db


@dataclass
class Theme:
    id: Optional[int]
    title: str


class ThemeModel(db.Model):
    __tablename__ = "themes"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode(), nullable=False, unique=True)


@dataclass
class Answer:
    title: str
    is_correct: bool


class AnswerModel(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer(), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete="CASCADE"))
    title = db.Column(db.Unicode(), nullable=False)
    is_correct = db.Column(db.Boolean(), nullable=False)


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]


class QuestionModel(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode(), nullable=False, unique=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id', ondelete="CASCADE"), nullable=False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._answers: list[AnswerModel] = list()

    @property
    def answers(self) -> list[AnswerModel]:
        return self._answers

    @answers.setter
    def answers(self, val: Optional[AnswerModel]):
        if val is not None:
            self._answers.append(val)

