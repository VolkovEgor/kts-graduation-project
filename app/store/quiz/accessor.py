from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Theme,
    Question,
    Answer,
    ThemeModel,
    QuestionModel,
    AnswerModel,
)
from typing import List


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = await ThemeModel.create(
            title=title
        )
        return Theme(
            id=theme.id,
            title=theme.title,
        )

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        themes = await ThemeModel.query.where(ThemeModel.title == title).gino.all()
        if len(themes) > 0:
            return Theme(
                id=themes[0].id,
                title=themes[0].title,
            )
        return None

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        themes = await ThemeModel.query.where(ThemeModel.id == id_).gino.all()
        if len(themes) > 0:
            return Theme(
                id=themes[0].id,
                title=themes[0].title,
            )
        return None

    async def list_themes(self) -> List[Theme]:
        raw_themes = await ThemeModel.query.gino.all()
        themes = []

        for raw_theme in raw_themes:
            themes.append(
                Theme(
                    id=raw_theme.id,
                    title=raw_theme.title,
                )
            )
        return themes

    async def create_answers(self, question_id, answers: List[Answer]):
        for answer in answers:
            await AnswerModel.create(
                question_id=question_id,
                title=answer.title,
                is_correct=answer.is_correct,
            )

    async def create_question(
            self, title: str, theme_id: int, answers: List[Answer]
    ) -> Question:
        question = await QuestionModel.create(
            title=title,
            theme_id=theme_id
        )
        await self.create_answers(question_id=question.id, answers=answers)
        return Question(
            id=question.id,
            title=question.title,
            theme_id=theme_id,
            answers=answers,
        )

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        questions = await (
            QuestionModel.outerjoin(AnswerModel, QuestionModel.id == AnswerModel.question_id)
            .select()
            .where(QuestionModel.title == title)
            .gino
            .load(QuestionModel.distinct(QuestionModel.id).load(answers=AnswerModel.distinct(AnswerModel.id)))
            .all()
        )

        if len(questions):
            answers = []
            if len(questions[0].answers) > 0:
                for raw_answer in questions[0].answers:
                    answer = Answer(
                        title=raw_answer.title,
                        is_correct=raw_answer.is_correct,
                    )
                    answers.append(answer)

            return Question(
                id=questions[0].id,
                title=questions[0].title,
                theme_id=questions[0].theme_id,
                answers=answers,
            )
        return None

    async def list_questions(self, theme_id: Optional[int] = None) -> List[Question]:
        if theme_id is None:
            raw_questions = await (
                QuestionModel.outerjoin(AnswerModel, QuestionModel.id == AnswerModel.question_id)
                .select()
                .gino
                .load(QuestionModel.distinct(QuestionModel.id).load(answers=AnswerModel.distinct(AnswerModel.id)))
                .all()
            )
        else:
            raw_questions = await (
                QuestionModel.outerjoin(AnswerModel, QuestionModel.id == AnswerModel.question_id)
                .select()
                .where(QuestionModel.theme_id == theme_id)
                .gino
                .load(QuestionModel.distinct(QuestionModel.id).load(answers=AnswerModel.distinct(AnswerModel.id)))
                .all()
            )

        questions = []
        if len(raw_questions) > 0:
            for i, raw_question in enumerate(raw_questions):
                answers = []
                if len(raw_question.answers) > 0:
                    for raw_answer in raw_question.answers:
                        answer = Answer(
                            title=raw_answer.title,
                            is_correct=raw_answer.is_correct,
                        )
                        answers.append(answer)
                questions.append(
                    Question(
                        id=raw_question.id,
                        title=raw_question.title,
                        theme_id=raw_question.theme_id,
                        answers=answers,
                    )
                )

        return questions
