import os
import uuid
from typing import Optional

from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

from app.contant_manager import (chunking_prompt_ar, simplify_prompt_ar,
                                 EMBEDDING_MODEL, question_generation_prompt_ar)
from app.models.llm_response_model import (ChunkResults, TextProcessingResult,
                                           VideoText, QuizModel, QuizResponse)


class OpenAITextProcessor:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", max_workers: int = 5):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def get_embed(self, arabic_text: str):
        embed = self.client.embeddings.create(
            input=arabic_text,
            model=EMBEDDING_MODEL
        )

        return embed.data[0].embedding

    def process_video_sync(self, video: str) -> VideoText:
        """Synchronous function to handle OpenAI request in a blocking way"""
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": chunking_prompt_ar},
                    {"role": "user", "content": video}
                ],
                temperature=0,
                response_format=ChunkResults
            )
            video_id = uuid.uuid4()
            paragraph_id = uuid.uuid4()
            return VideoText(
                video=video,
                video_id=str(video_id),
                paragraph=response.choices[0].message.parsed.chunks,
                paragraph_id=str(paragraph_id),
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
        except Exception as e:
            raise e

    def process_video(self, video: str):
        """Submit the task to the thread pool for asynchronous execution"""
        return self.executor.submit(self.process_video_sync, video)

    def simplify(self, paragraph: str) -> tuple[TextProcessingResult, int, int, int]:
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": paragraph},
                    {"role": "user", "content": simplify_prompt_ar}
                ],
                temperature=0,
                response_format=TextProcessingResult
            )
            return (
                response.choices[0].message.parsed,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                response.usage.total_tokens,
            )
        except Exception as e:
            raise e

    def generate_quiz(self, paragraph_content, paragraph_id: str) -> tuple[list[QuizModel], int, int, int]:
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": question_generation_prompt_ar},
                    {"role": "user", "content": paragraph_content}
                ],
                temperature=0,
                response_format=QuizResponse
            )
            tokens = response.usage.total_tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            return response.choices[0].message.parsed.quiz, input_tokens, output_tokens, tokens
        except Exception as e:
            raise e

