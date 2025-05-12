import os
import uuid
from typing import Optional

from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from app.contant_manager import EMBEDDING_MODEL, paragraph_generator, simplify_prompt, question_generation_prompt
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
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=paragraph_generator
                    ),
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=video
                    )
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
                paragraph_id=str(paragraph_id)
            )
        except Exception as e:
            raise e

    def process_video(self, video: str):
        """Submit the task to the thread pool for asynchronous execution"""
        return self.executor.submit(self.process_video_sync, video)

    def simplify(self, paragraph: str, language: str) -> TextProcessingResult | None:
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=simplify_prompt
                    ),
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=f"##Script: {paragraph}\n##\n##Answer in {language} language:\n##\n"
                    )
                ],
                temperature=0,
                response_format=TextProcessingResult
            )
            return response.choices[0].message.parsed
        except Exception as e:
            raise e

    def generate_quiz(self, paragraph_content) -> list[QuizModel]:
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=question_generation_prompt
                    ),
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=paragraph_content
                    )
                ],
                temperature=0,
                response_format=QuizResponse
            )
            return response.choices[0].message.parsed.quiz
        except Exception as e:
            raise e

