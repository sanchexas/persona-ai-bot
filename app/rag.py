import os
import asyncio
from typing import List
from sqlalchemy import select
from db import AsyncSessionLocal, PersonaLore
from dotenv import load_dotenv
# from client import openai_client
from db import add_lore_to_db
from fastembed import TextEmbedding
from logger import logger

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

def _generate_embedding_sync(text: str) -> List[float]:
    logger.debug(f"Generating embedding for text: '{text[:40]}...'")
    embeddings = list(embedding_model.embed([text]))
    return embeddings[0].tolist()

async def get_embedding(text: str) -> List[float]:
    """Text to vector"""
    # response = await openai_client.embeddings.create(
    #     model="openai/text-embedding-3-small",
    #     input=text
    # )
    # return response.data[0].embedding
    return await asyncio.to_thread(_generate_embedding_sync, text=text)

async def get_relevant_lore(user_query: str, limit: int = 2, threshold: float = 0.55) -> List[str]:
    """
    Finds the most similar facts from a person's biography  
    using the cosine distance of the vectors.
    """
    try:
        query_vector = await get_embedding(user_query)

        async with AsyncSessionLocal() as session:
            # Searching for the closest vectors via cosine_distance
            distance_expr = PersonaLore.embedding.cosine_distance(query_vector)
            query = (
                select(PersonaLore.content)
                .where(distance_expr < threshold)
                .order_by(distance_expr)
                .limit(limit)
            )
            result = await session.execute(query)
            relevant_facts = [row[0] for row in result.all()]

            logger.debug(f"RAG PersonaLore retrieved | count={len(relevant_facts)}")
            return relevant_facts
    except Exception as e:
        logger.error(f"Failed to extract persona lore for query '{user_query[:30]}...': {e}", exc_info=True)
        return []

async def add_lore_fact(content: str, category: str = "general") -> bool:
    try:
        logger.debug(f"Adding new persona lore fact: '{content}'")
        vector = await get_embedding(content)
        return await add_lore_to_db(content=content, category=category, embedding=vector)
    except Exception as e:
        logger.error(f"Failed to add persona lore fact: {e}", exc_info=True)
        return False