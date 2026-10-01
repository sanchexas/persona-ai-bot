import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from config import config
from db import add_message, get_recent_history

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
LLM_MODEL = os.getenv("LLM_MODEL")

async def generate_response(chat_id: int, user_message: str) -> str:

    await add_message(chat_id=chat_id, role="user", content=user_message)

    history_limit = config.get("llm_settings", {}).get("history_limit", 10)
    history = await get_recent_history(chat_id=chat_id, limit=history_limit)

    messages = [
        {
            "role": "system",
            "content": config["persona_prompt"],
        },
        *history
    ]

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages
    )

    ai_response = response.choices[0].message.content

    await add_message(chat_id=chat_id, role="assistant", content=ai_response)

    return ai_response