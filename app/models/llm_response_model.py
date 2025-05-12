from typing import List, Optional

from pydantic import BaseModel, Field


class ChunkResults(BaseModel):
    chunks: list[str]


class VideoText(BaseModel):
    video: str = Field(..., description="Video text")
    video_id: str = Field(..., description="Video ID")
    paragraph: list[str] = Field(..., description="List of paragraphs in the video")
    paragraph_id: str = Field(..., description="Paragraph ID")


class SkillsModel(BaseModel):
    skill: str = Field(..., description="Skill of the paragraph")
    skill_id: str = Field(..., description="Skill ID")
    paragraph_id: str = Field(..., description="Paragraph ID")


class ObjectiveModel(BaseModel):
    objective: str = Field(..., description="Objective of the paragraph")
    objective_id: str = Field(..., description="Objective ID")
    paragraph_id: str = Field(..., description="Paragraph ID")


class TextProcessingResult(BaseModel):
    original_paragraph: str = Field(..., description="Corrected paragraph")
    simplify1: str = Field(..., description="Basic explanation")
    simplify2: str = Field(..., description="More simplified explanation")
    simplify3: str = Field(..., description="Child-friendly explanation")


class AnswerModel(BaseModel):
    question_id: str = Field(..., description="The question ID")
    answer: str = Field(..., description="Answer option")
    # answer_id: str = Field(..., description="uuid.uuid4() answer ID")


class AlternativeQuestion(BaseModel):
    question: str = Field(..., description="Alternative question")
    question_id: str = Field(..., description="uuid.uuid4() alternative question ID")
    answer: List[AnswerModel] = Field(..., description="List of answer options [A, B, C, D] or [True, False]")
    correct_answer: str = Field(..., description="Correct answer")
    # correct_answer_id: str = Field(..., description="uuid.uuid4() correct answer ID")


class QuizSkillsAndObjectiveModel(BaseModel):
    question_id: str = Field(..., description="The question ID")
    skill: str = Field(..., description="Skill of the paragraph")
    skill_id: str = Field(..., description="Skill ID")
    objective: str = Field(..., description="Objective of the paragraph")
    objective_id: str = Field(..., description="Objective ID")


class QuizModel(BaseModel):
    question: str = Field(..., description="Quiz question")
    question_id: str = Field(..., description="uuid.uuid4() question ID")
    answer: List[AnswerModel] = Field(..., description="List of answer options [A, B, C, D] or [True, False]")
    correct_answer: str = Field(..., description="Correct answer")
    # correct_answer_id: str = Field(..., description="uuid.uuid4() correct answer ID")
    alternative_questions: List[AlternativeQuestion] = Field(..., description="List of alternative questions")
    question_skills_and_objective: List[QuizSkillsAndObjectiveModel] = Field(...,
                                                                             description="List of skills related to the question")


class QuizResponse(BaseModel):
    quiz: List[QuizModel] = Field(..., description="Generated quiz for the paragraph")


class TextProcessingSchema(TextProcessingResult):
    paragraph_id: str = Field(..., description="Paragraph ID")
    original_paragraph_id: str = Field(..., description="Original paragraph ID")
    simplify1_id: str = Field(..., description="Basic explanation")
    simplify2_id: str = Field(..., description="More simplified explanation")
    simplify3_id: str = Field(..., description="Child-friendly explanation")


class ParagraphWithSkills(BaseModel):
    paragraph_id: str = Field(..., description="Paragraph ID")
    simplified: TextProcessingSchema
    skills: List[SkillsModel]
    objectives: List[ObjectiveModel]
    quiz: Optional[List[QuizModel]] = Field(None, description="Generated quiz for the paragraph")
    # quiz: Optional[List[Dict]] = Field(None, description="Generated quiz for the paragraph")


class SimplifyResponse(BaseModel):
    video: str = Field(..., description="Video text")
    paragraph: list[ParagraphWithSkills] = Field(..., description="List of simplified paragraphs with related skills")


class LearningKitResponse(BaseModel):
    results: List[SimplifyResponse]
