import os
import uuid
from typing import List

from dotenv import load_dotenv

from app.client.llm_client import OpenAITextProcessor
from app.models.processing_models import ProcessedParagraph, SimplifyResults, QuizResults
from app.schema.video_schema import VideoRequestSchema

load_dotenv()
llm_client = OpenAITextProcessor(os.getenv(" "), model="gpt-4o", max_workers=5)


def get_paragraph(video: VideoRequestSchema) -> List[ProcessedParagraph]:
    try:
        paragraph_with_id = []
        response = llm_client.get_paragraph(objective=video.objective,
                                            skills=video.skills,
                                            video=video.video)
        print(len(response.paragraph))
        for paragraph in response.paragraph:
            paragraph_with_id.append(ProcessedParagraph(
                video_id=str(video.video_id),
                paragraph=paragraph.paragraph,
                paragraph_id=str(uuid.uuid4()),
                skills=paragraph.related_skills,
                objective=paragraph.related_objectives,
                language=video.language,
            ))
        return paragraph_with_id
    except Exception as e:
        raise e


def simplify_paragraph_v1(paragraph: List[ProcessedParagraph]) -> List[SimplifyResults]:
    try:
        simplify_result_list = []
        for paragraph in paragraph:
            simplify_results = llm_client.simplify(paragraph.paragraph)
            simplify_result_list.append(SimplifyResults(
                video_id=paragraph.video_id,
                paragraph=paragraph.paragraph,
                paragraph_id=paragraph.paragraph_id,
                simplify1=simplify_results.simplify1,
                simplify1_id=str(uuid.uuid4()),
                simplify2=simplify_results.simplify2,
                simplify2_id=str(uuid.uuid4()),
                simplify3=simplify_results.simplify3,
                simplify3_id=str(uuid.uuid4()),
                skills=paragraph.skills,
                objective=paragraph.objective,
                language=paragraph.language
            ))
        return simplify_result_list
    except Exception as e:
        raise e


def generate_quiz(paragraph: List[SimplifyResults]):
    try:
        quiz_result_list = []
        for paragraph in paragraph:
            quiz_results = llm_client.generate_quiz(skills=paragraph.skills,
                                                    objective=paragraph.objective,
                                                    paragraph_content=paragraph.paragraph)
            quiz_result_list.append(QuizResults(
                video_id=paragraph.video_id,
                paragraph=paragraph.paragraph,
                paragraph_id=paragraph.paragraph_id,
                simplify1=paragraph.simplify1,
                simplify1_id=paragraph.simplify1_id,
                simplify2=paragraph.simplify2,
                simplify2_id=paragraph.simplify2_id,
                simplify3=paragraph.simplify3,
                simplify3_id=paragraph.simplify3_id,
                quiz=quiz_results.quiz,
                skills=paragraph.skills,
                objective=paragraph.objective,
                language=paragraph.language
            )
            )
        return quiz_result_list
    except Exception as e:
        raise e
