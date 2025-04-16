import os
import uuid
from copy import copy
from typing import List, Any

from app.client.llm_client import OpenAITextProcessor
from app.client.vector_db import QdrantDBClient
from app.models.llm_response_model import VideoText, SimplifyResponse, TextProcessingResult, SkillsModel, \
    ParagraphWithSkills, ObjectiveModel, TextProcessingSchema
from dotenv import load_dotenv

from app.models.schema import SimplifyResponseSchema

load_dotenv()
llm_client = OpenAITextProcessor(os.getenv("OPENAI_API_KEY"), model="gpt-4o", max_workers=5)
vectordb_client = QdrantDBClient(host='localhost', port=6333)


def chunk_course(videos) -> dict[str, int | list[VideoText] | Any]:
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    # Submit the sections to the thread pool with indices to preserve order
    futures = {i: llm_client.process_video(section) for i, section in enumerate(videos)}

    # Collect results in the order they were submitted
    results: List[VideoText] = [None] * len(videos)
    for i, future in futures.items():
        result = future.result()
        input_tokens += result.input_tokens
        output_tokens += result.output_tokens
        total_tokens += result.total_tokens
        results[i] = result

    print(f"Total input tokens: {input_tokens}")
    print(f"Total output tokens: {output_tokens}")
    print(f"Total tokens: {total_tokens}")
    return {
        "results": results,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

def simplify_paragraph(videos: List[VideoText]) -> dict[str, int | list[SimplifyResponseSchema] | Any]:
    try:
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        simplify_results: List[SimplifyResponseSchema] = []

        print(f"Starting simplification for {len(videos)} videos...\n")

        for video_index, video in enumerate(videos):
            print(f"\n📹 Processing video {video_index + 1}: {video.video[:60]}...")

            paragraph_list = video.paragraph
            if not paragraph_list:
                print("⚠️ No paragraphs found in this video. Skipping.")
                continue

            print(f"🔍 Found {len(paragraph_list)} paragraphs. Simplifying...")

            # Submit simplification tasks in parallel
            simplify_futures = {
                i: llm_client.executor.submit(llm_client.simplify, paragraph)
                for i, paragraph in enumerate(paragraph_list)
            }

            simplified_results: List[TextProcessingSchema] = [None] * len(paragraph_list)
            skill_results: List[List[SkillsModel]] = [None] * len(paragraph_list)
            objective_results: List[List[ObjectiveModel]] = [None] * len(paragraph_list)

            for i, future in simplify_futures.items():
                print(f"🧠 Simplifying paragraph {i + 1}/{len(paragraph_list)}")
                simplified, in_tok, out_tok, total_tok = future.result()

                input_tokens += in_tok
                output_tokens += out_tok
                total_tokens += total_tok

                print(f"🔍 Simplified result {i + 1}: {simplified}")
                simplified = simplified.model_dump()
                simplified["paragraph_id"] = video.paragraph_id
                simplified["original_with_tashkeel_id"] = str(uuid.uuid4())
                simplified["simplify1_id"] = str(uuid.uuid4())
                simplified["simplify2_id"] = str(uuid.uuid4())
                simplified["simplify3_id"] = str(uuid.uuid4())
                simplified_results[i] = TextProcessingSchema(**simplified)

                simplified_text = simplified["simplify1"]
                print(f"🧲 Getting similar skills for simplified text {i + 1}")
                skill_results[i] = get_similar_skills(simplified_text, video.paragraph_id)
                objective_results[i] = get_similar_objectives(simplified_text, video.paragraph_id)
                print(f"✅ Found {len(skill_results[i])} similar skills.")

            simplify_results.append(
                SimplifyResponseSchema(
                    video=video.video,
                    paragraph_id=video.paragraph_id,
                    video_id=video.video_id,
                    paragraph=[
                        ParagraphWithSkills(
                            paragraph_id=video.paragraph_id,
                            simplified=simplified_results[i],
                            skills=skill_results[i],
                            objectives=objective_results[i]
                        )
                        for i in range(len(paragraph_list))
                    ]
                )
            )

            print(f"✅ Finished processing video {video_index + 1}\n")

        print("🎉 All videos processed.")
        print(f"📊 Total tokens used → Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")

        return {
            "results": simplify_results,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }


    except Exception as e:
        print("❌ Error occurred:", str(e))
        raise e

def get_similar_skills(paragraph: str, paragraph_id: str) -> list[SkillsModel]:
    try:
        embedding = llm_client.get_embed(paragraph)
        skills_result = vectordb_client.query(
            collection_name='skills',
            vector=embedding,
            limit=1
        )
        skills_list: List[SkillsModel] = []
        for item in skills_result:
            skill_id = item.id
            skill_en = item.payload.get('skill_en')
            skills_list.append(
                SkillsModel(
                    skill_en=skill_en,
                    skill_id=skill_id,
                    paragraph_id=paragraph_id
                )
            )
        return skills_list
    except Exception as e:
        raise e

def get_similar_objectives(paragraph: str, paragraph_id: str) -> list[ObjectiveModel]:
    try:
        embedding = llm_client.get_embed(paragraph)
        objectives_result = vectordb_client.query(
            collection_name='objective',
            vector=embedding,
            limit=2
        )
        objectives_list: List[ObjectiveModel] = []
        for item in objectives_result:
            objective_id = item.id
            objective_en = item.payload.get('objective_en')
            objectives_list.append(
                ObjectiveModel(
                    objective_en=objective_en,
                    objective_id=objective_id,
                    paragraph_id=paragraph_id
                )
            )
        return objectives_list
    except Exception as e:
        raise e


def generate_quiz(simplify_results: List[SimplifyResponseSchema]) -> dict:
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    for video in simplify_results:
        for paragraph in video.paragraph:
            skills_list = []
            objective_list = []

            for skills in paragraph.skills:
                skills_list.append({
                    "skill_id": skills.skill_id,
                    "skill_en": skills.skill_en,
                })
            for objective in paragraph.objectives:
                objective_list.append({
                    "objective_id": objective.objective_id,
                    "objective_en": objective.objective_en,
                })

            print(f"📝 Generating quiz for paragraph: {paragraph.simplified.original_with_tashkeel}")

            paragraph_with_skills = (
                "# Available skills: " + str(skills_list) + "\n\n" +
                "# Available objectives: " + str(objective_list) + "\n\n" +
                "# Paragraph: " + paragraph.simplified.original_with_tashkeel + "\n"
            )

            quiz, in_tokens, out_tokens, tokens = llm_client.generate_quiz(paragraph_with_skills, paragraph_id=paragraph.paragraph_id)

            input_tokens += in_tokens
            output_tokens += out_tokens
            total_tokens += tokens

            quiz_with_paragraph_id = []

            for q in quiz:
                q.question_id = str(uuid.uuid4())

                for skills in q.question_skills_and_objective:
                    skills.question_id = q.question_id
                for ans in q.answer:
                    ans.question_id = q.question_id
                for alter in q.alternative_questions:
                    alter.question_id = str(uuid.uuid4())
                    for ans in alter.answer:
                        ans.question_id = alter.question_id

                q = q.model_dump()
                q["paragraph_id"] = paragraph.paragraph_id
                quiz_with_paragraph_id.append(q)

            print(f"✅ Quiz generated: {quiz}")
            paragraph.quiz = quiz_with_paragraph_id

    print(f"📊 Quiz Token Usage → Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")

    return {
        "results": simplify_results,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


