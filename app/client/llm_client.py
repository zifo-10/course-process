import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from app.contant_manager import paragraph_generator, simplify_prompt, question_generation_prompt
from app.models.llm_response_model import ParagraphResponse, SimplifyResponse, QuizResponse


class OpenAITextProcessor:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", max_workers: int = 5):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def get_paragraph(self, video: str, skills: list, objective: list) -> ParagraphResponse | None:
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
                        content=f"##Script: {video}\n##Skills: {skills}\n##Objectives: {objective}\n##\n"
                    )
                ],
                temperature=0,
                response_format=ParagraphResponse
            )
            return response.choices[0].message.parsed
        except Exception as e:
            raise e

    def simplify(self, paragraph: str) -> SimplifyResponse | None:
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
                        content=f"##Script: {paragraph}\n##\n"
                    )
                ],
                temperature=0,
                response_format=SimplifyResponse
            )
            return response.choices[0].message.parsed
        except Exception as e:
            raise e

    def generate_quiz(self, paragraph_content, skills: list, objective: list) -> QuizResponse:
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
                        content=f"##Script: {paragraph_content}\n##Skills: {skills}\n##Objectives: {objective}\n##\n"
                    )
                ],
                temperature=0,
                response_format=QuizResponse
            )
            return response.choices[0].message.parsed
        except Exception as e:
            raise e
