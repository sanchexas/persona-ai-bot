import asyncio
import os
from dotenv import load_dotenv
from config import config
from db import add_message, get_recent_history, get_relevant_user_facts
from client import openai_client
from rag import get_embedding, get_relevant_lore
from user_memory import process_and_save_user_facts
from logger import logger

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")

async def generate_response(chat_id: int, user_message: str) -> str:
    # Save user message
    await add_message(chat_id=chat_id, role="user", content=user_message)
    # Extract and save personal facts about the interlocutor at the background
    asyncio.create_task(process_and_save_user_facts(chat_id, user_message))
    # Generate vector for user message
    query_embedding = await get_embedding(user_message)
    # Request persona lore and facts about the user in parallel
    relevant_facts, user_facts = await asyncio.gather(
        get_relevant_lore(user_message, limit=2, threshold=0.55),
        get_relevant_user_facts(chat_id, query_embedding, limit=3, threshold=0.55)
    )
    system_prompt = config.get("persona_prompt", "")

    if relevant_facts:
        facts_list = "\n".join(f"- {fact}" for fact in relevant_facts)
        lore_template = config.get("rag_lore_facts_template")
        system_prompt += f"\n{lore_template}\n{facts_list}"
        logger.debug(f"Added Lore facts to prompt for chat_id={chat_id}: {relevant_facts}")
    if user_facts:
        user_facts_list = "\n".join(f"- {fact}" for fact in user_facts)
        user_template = config.get("user_facts_template")
        system_prompt += f"\n{user_template}\n{user_facts_list}"
        logger.debug(f"Added User facts to prompt for chat_id={chat_id}: {user_facts}")

    history_limit = config.get("llm_settings", {}).get("history_limit", 10)
    history = await get_recent_history(chat_id=chat_id, limit=history_limit)

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