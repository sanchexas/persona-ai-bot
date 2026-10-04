import json
import os
from dotenv import load_dotenv

from client import openai_client
from db import add_user_fact
from rag import get_embedding
from logger import logger

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL")

EXTRACTION_PROMPT = """
Analyze the user's remark and determine whether it contains long-term personal facts about the user himself (his name, profession, habits, preferences, biography, details of life).

Rules:
1. If THERE are NO facts (the usual greeting, question, abstract reasoning, emotion) — return an empty list [].
2. If there are facts, formulate them in the form of short statements from the 3rd person in the LANGUAGE IN WHICH THE USER TEXTING YOU (for example: "Loves cappuccino without sugar", "Works as a developer", "Lives in Batumi").
3. Ignore one—time/ situational actions (for example: "I went to the store", "I'm cold right now").

Return the result STRICTLY in JSON format:
{"facts": ["fact 1", "fact 2"]}
"""

async def extract_facts_from_message(user_message: str) -> list[str]:
    """Analyzes the user's message and returns a list of highlighted facts."""
    try:
        response = await openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        facts = data.get("facts", [])
        if facts:
            logger.debug(f"Extracted user facts:\n{facts}")
        return facts
    except Exception as e:
        logger.error(f"Failed to extract user facts: {e}", exc_info=True)
        return []

async def process_and_save_user_facts(chat_id: int, user_message: str):
    """Extracts facts from a message, vectorizes them, and stores them in the user_facts table."""
    facts = await extract_facts_from_message(user_message)
    for fact in facts:
        embedding = await get_embedding(fact)
        await add_user_fact(chat_id=chat_id, fact=fact, embedding=embedding)