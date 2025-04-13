from pydantic import BaseModel, Field

from app.models.llm_response_model import SimplifyResponse, TextProcessingResult


class SimplifyResponseSchema(SimplifyResponse):
    paragraph_id: str = Field(..., description="Paragraph ID")
    video_id: str = Field(..., description="Video ID")



