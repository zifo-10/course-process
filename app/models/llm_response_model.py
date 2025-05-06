import uuid
from typing import List

from pydantic import BaseModel, Field, model_validator

from app.schema.video_schema import MetaDataSchema


class ParagraphMetaData(BaseModel):
    paragraph: str = Field(..., description="Paragraph text")
    related_skills: List[MetaDataSchema] = Field(..., description="List of skills related to the paragraph")
    related_objectives: List[MetaDataSchema] = Field(..., description="List of objectives related to the paragraph")


class ParagraphResponse(BaseModel):
    paragraph: List[ParagraphMetaData] = Field(..., description="List of paragraphs in the video")


class SimplifyResponse(BaseModel):
    simplify1: str = Field(..., description="Basic explanation")
    simplify2: str = Field(..., description="More simplified explanation")
    simplify3: str = Field(..., description="Child-friendly explanation")


class AlternativeQuestion(BaseModel):
    question: str = Field(..., description="Alternative question")
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                             description="Unique UUID for the alternative question")
    options: List[str] = Field(..., description="List of answer options [A, B, C, D] or [True, False]")
    correct_answer: str = Field(..., description="Correct answer")

    @model_validator(mode='before')
    def generate_question_id(cls, values):
        # Ensure that question_id is set if not provided
        if 'question_id' not in values:
            values['question_id'] = str(uuid.uuid4())
        return values


class QuizMetaData(BaseModel):
    question: str = Field(..., description="Quiz question")
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                             description="Unique UUID for the alternative question")
    options: List[str] = Field(..., description="List of quiz responses")
    correct_answer: str = Field(..., description="Correct answer")
    related_skills: List[MetaDataSchema] = Field(..., description="List of skills related to the quiz")
    related_objectives: List[MetaDataSchema] = Field(..., description="List of objectives related to the quiz")
    alternative_questions: List[AlternativeQuestion] = Field(..., description="List of alternative questions")

    @model_validator(mode='before')
    def generate_question_id(cls, values):
        # Ensure that question_id is set if not provided
        if 'question_id' not in values:
            values['question_id'] = str(uuid.uuid4())
        return values


class QuizResponse(BaseModel):
    quiz: List[QuizMetaData] = Field(..., description="Generated quiz for the paragraph")
