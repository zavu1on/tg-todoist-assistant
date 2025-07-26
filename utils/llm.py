from datetime import datetime
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from assets import text
from config.core import Config


def get_time_context() -> str:
    return f"Сегодняшня дата и время: {datetime.now()}, день недели: {datetime.now().strftime('%A')}, неделя начинается с Monday"


class LLM:

    def __init__(self, secret_key: str):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=secret_key,
        )

    async def generate_response(
            self,
            message: str,
            role: str,
            temperature: float = 0.3
    ) -> ChatCompletion:
        return await self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://t.me/todoist_ai_assistant_bot",
                "X-Title": "Todoist Assistant",
            },
            extra_body={},
            model=Config.MODEL,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": role + get_time_context(),
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

    async def get_add_todo_data(self, message: str) -> str:
        resp = await self.generate_response(
            message=message,
            role=text.ADD_TASK_PROMPT
        )
        return resp.choices[0].message.content


llm = LLM(secret_key=Config.OPENROUTER_API_KEY)
