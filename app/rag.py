import os
from typing import List
from sqlalchemy import select
from db import AsyncSessionLocal, PersonaLore
from dotenv import load_dotenv
# from client import openai_client
from db import add_lore_to_db
from fastembed import TextEmbedding

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

async def get_embedding(text: str) -> List[float]:
    """Text to vector"""
    # response = await openai_client.embeddings.create(
    #     model="openai/text-embedding-3-small",
    #     input=text
    # )
    # return response.data[0].embedding
    embeddings = list(embedding_model.embed([text]))
    return embeddings[0].tolist()

async def get_relevant_lore(user_query: str, limit: int = 2, threshold: float = 0.55) -> List[str]:
    """
    Finds the most similar facts from a person's biography  
    using the cosine distance of the vectors.
    """
    try:
        query_vector = await get_embedding(user_query)

        async with AsyncSessionLocal() as session:
            distance_expr = PersonaLore.embedding.cosine_distance(query_vector)
            # Ищем ближайшие векторы через cosine_distance
            query = (
                select(PersonaLore.content)
                .where(distance_expr < threshold)
                .order_by(PersonaLore.embedding.cosine_distance(query_vector))
                .limit(limit)
            )
            result = await session.execute(query)
            relevant_facts = [row[0] for row in result.all()]
            
            return relevant_facts
    except Exception as e:
        print(f"[RAG Error] Couldn't extract lore: {e}")
        return []

async def add_lore_fact(content: str, category: str = "general") -> bool:
    try:
        vector = await get_embedding(content)
        return await add_lore_to_db(content=content, category=category, embedding=vector)
    except Exception as e:
        print(f"[RAG Error] Couldn't generate embedding for lore: {e}")
        return False