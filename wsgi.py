from typing import List, Any, Coroutine

from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO
import json
import os
from app.models.llm_response_model import SimplifyResponse, LearningKitResponse
from app.service.course_service import chunk_course, simplify_paragraph, generate_quiz
from app.utils.text_spillter import read_docx

app = FastAPI()

@app.post("/process_skills_obj")
async def process_skills_obj(skills_list: List[str], objective_list: List[str]) -> dict:
    try:
        # For example, you can save them to a database or perform some operations
        return {"skills": skills_list, "objectives": objective_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prepare-learning-kit/{language}")
async def upload_docx(language: str, file: UploadFile = File(...)) -> LearningKitResponse:
    try:

        file_content = BytesIO(await file.read())
        videos = read_docx(file_content)
        chunk_results = chunk_course(videos)

        simplify_result = simplify_paragraph(chunk_results, language)

        quiz_result = generate_quiz(simplify_result, language)

        # ✅ Create final response
        final_response = LearningKitResponse(
            results=quiz_result,
        )

        # ✅ Save to JSON file
        output_dir = "learning_kits"
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, f"response.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(final_response.model_dump(), f, ensure_ascii=False, indent=4)

        return final_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
