import uuid
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.llm_response_model import QuizMetaData
from app.schema.video_schema import MetaDataSchema


class ProcessedParagraph(BaseModel):
    video_id: Optional[str] = Field(uuid.uuid4(), description="Video ID")
    skills: List[MetaDataSchema] = Field(..., description="List of skills associated with the video")
    objective: List[MetaDataSchema] = Field(..., description="Objective of the video")
    language: str = Field(..., description="Language of the video")
    paragraph_id: str
    paragraph: str = Field(..., description="Paragraph text")


class SimplifyResults(ProcessedParagraph):
    simplify1_id: str
    simplify1: str = Field(..., description="Basic explanation")
    simplify2_id: str
    simplify2: str = Field(..., description="More simplified explanation")
    simplify3_id: str
    simplify3: str = Field(..., description="Child-friendly explanation")


class QuizResults(SimplifyResults):
    quiz: List[QuizMetaData]