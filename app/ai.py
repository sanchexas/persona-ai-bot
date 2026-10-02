import os
from dotenv import load_dotenv
from config import config
from db import add_message, get_recent_history
from client import openai_client
from rag import get_relevant_lore

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")

async def generate_response(chat_id: int, user_message: str) -> str:
    # Save user message
    await add_message(chat_id=chat_id, role="user", content=user_message)
    # Load messages history from database
    history_limit = config.get("llm_settings", {}).get("history_limit", 10)
    history = await get_recent_history(chat_id=chat_id, limit=history_limit)
    # Get relevant facts
    relevant_facts = await get_relevant_lore(user_message, limit=2, threshold=0.55)

    system_prompt = config["persona_prompt"]

    if relevant_facts:
        facts_list = "\n".join(f"- {fact}" for fact in relevant_facts)
        lore_block = (
            "\n\n=== КОНТЕКСТ ИЗ ТВОЕЙ ЖИЗНИ / ПАМЯТИ ===\n"
            f"{facts_list}\n"
            "Используй эти факты органично в ответе, ТОЛЬКО если они уместны к вопросу. "
            "Не цитируй их дословно, а отвечай от своего лица."
        )
        system_prompt += lore_block

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        *history
    ]
    # LLM query
    response = await openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages
    )

    ai_response = response.choices[0].message.content
    # Save assistant's response to database
    await add_message(chat_id=chat_id, role="assistant", content=ai_response)

    return ai_response