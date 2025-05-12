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
vectordb_client = QdrantDBClient(host=os.getenv("QDRANT_URL"), port=6333)


def chunk_course(videos) -> list[VideoText]:

    # Submit the sections to the thread pool with indices to preserve order
    futures = {i: llm_client.process_video(section) for i, section in enumerate(videos)}

    # Collect results in the order they were submitted
    results: List[VideoText] = [None] * len(videos)
    for i, future in futures.items():
        result = future.result()
        results[i] = result
    return results

def simplify_paragraph(videos: List[VideoText], language: str) -> list[SimplifyResponseSchema]:
    try:
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
                i: llm_client.executor.submit(llm_client.simplify, paragraph, language)
                for i, paragraph in enumerate(paragraph_list)
            }

            simplified_results: List[TextProcessingSchema] = [None] * len(paragraph_list)
            skill_results: List[List[SkillsModel]] = [None] * len(paragraph_list)
            objective_results: List[List[ObjectiveModel]] = [None] * len(paragraph_list)

            for i, future in simplify_futures.items():
                print(f"🧠 Simplifying paragraph {i + 1}/{len(paragraph_list)}")
                simplified = future.result()

                print(f"🔍 Simplified result {i + 1}: {simplified}")
                simplified = simplified.model_dump()
                simplified["paragraph_id"] = video.paragraph_id
                simplified["original_paragraph_id"] = str(uuid.uuid4())
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

        return simplify_results


    except Exception as e:
        print("❌ Error occurred:", str(e))
        raise e

def get_similar_skills(paragraph: str, paragraph_id: str) -> list[SkillsModel]:
    try:
        embedding = llm_client.get_embed(paragraph)
        skills_result = vectordb_client.query(
            collection_name='skills-haj',
            vector=embedding,
            limit=1
        )
        skills_list: List[SkillsModel] = []
        for item in skills_result:
            skill_id = item.id
            skill = item.payload.get('skills')
            skills_list.append(
                SkillsModel(
                    skill=skill,
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
            collection_name='objectives-haj',
            vector=embedding,
            limit=2
        )
        objectives_list: List[ObjectiveModel] = []
        for item in objectives_result:
            objective_id = item.id
            objective = item.payload.get('objectives')
            objectives_list.append(
                ObjectiveModel(
                    objective=objective,
                    objective_id=objective_id,
                    paragraph_id=paragraph_id
                )
            )
        return objectives_list
    except Exception as e:
        raise e


from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

def generate_quiz(simplify_results: List[SimplifyResponseSchema], language: str) -> List[SimplifyResponseSchema]:
    tasks = []
    executor = ThreadPoolExecutor(max_workers=10)  # Adjust based on your system's capacity

    def build_prompt(paragraph):
        skills_list = [{"skill_id": s.skill_id, "skill": s.skill} for s in paragraph.skills]
        objective_list = [{"objective_id": o.objective_id, "objective": o.objective} for o in paragraph.objectives]

        return (
            "# Available skills: " + str(skills_list) + "\n\n"
            "# Available objectives: " + str(objective_list) + "\n\n"
            "# Paragraph: " + paragraph.simplified.original_paragraph + "\n"
            f"Answer in {language} language:\n"
        )

    # Collect all tasks
    for video in simplify_results:
        for paragraph in video.paragraph:
            prompt = build_prompt(paragraph)
            print(f"📝 Generating quiz for paragraph: {paragraph.simplified.original_paragraph}")
            future = executor.submit(llm_client.generate_quiz, prompt)
            tasks.append((future, paragraph))  # preserve paragraph reference

    # Apply results in the original order
    for future, paragraph in tasks:
        paragraph.quiz = future.result()

    executor.shutdown(wait=True)
    return simplify_results



