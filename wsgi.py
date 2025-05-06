from typing import List

from fastapi import FastAPI, HTTPException

from app.models.processing_models import QuizResults
from app.schema.video_schema import VideoRequestSchema
from app.service.course_service import generate_quiz, get_paragraph, \
    simplify_paragraph_v1

app = FastAPI()


@app.post("/v1/prepare-learning-kit/")
async def process_video(process_video_request: VideoRequestSchema) -> List[QuizResults]:
    try:
        # Generate paragraph
        paragraph_list = await get_paragraph(process_video_request)
        simplify = await simplify_paragraph_v1(paragraph_list)
        quiz = await generate_quiz(simplify)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

