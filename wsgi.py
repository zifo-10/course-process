from typing import List, Any, Coroutine

from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO
import json
import os
from app.models.llm_response_model import SimplifyResponse, LearningKitResponse
from app.service.course_service import chunk_course, simplify_paragraph, generate_quiz
from app.utils.text_spillter import read_docx

app = FastAPI()


@app.post("/prepare-learning-kit/")
async def upload_docx(file: UploadFile = File(...)) -> LearningKitResponse:
    try:
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0

        file_content = BytesIO(await file.read())
        videos = read_docx(file_content)
        chunk_results = chunk_course(videos)

        total_input_tokens += chunk_results['input_tokens']
        total_output_tokens += chunk_results['output_tokens']
        total_tokens += chunk_results['total_tokens']

        simplify_result = simplify_paragraph(chunk_results['results'])

        total_input_tokens += simplify_result['input_tokens']
        total_output_tokens += simplify_result['output_tokens']
        total_tokens += simplify_result['total_tokens']

        quiz_result = generate_quiz(simplify_result['results'])

        total_input_tokens += quiz_result['input_tokens']
        total_output_tokens += quiz_result['output_tokens']
        total_tokens += quiz_result['total_tokens']

        # ✅ Create final response
        final_response = LearningKitResponse(
            results=quiz_result['results'],
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_tokens=total_tokens
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
