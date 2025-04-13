from typing import List, Any, Coroutine

from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO

from app.models.llm_response_model import SimplifyResponse
from app.service.course_service import chunk_course, simplify_paragraph, generate_quiz
from app.utils.text_spillter import read_docx

app = FastAPI()

@app.post("/prepare-learning-kit/")
async def upload_docx(file: UploadFile = File(...)) -> list[SimplifyResponse]:
    try:
        # Read the file content into memory as BytesIO
        file_content = BytesIO(await file.read())

        # Process the docx content and get sections
        videos = read_docx(file_content)

        chunk_results = chunk_course(videos)
        simplify_results = simplify_paragraph(chunk_results)
        final_results = generate_quiz(simplify_results)

        return final_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
