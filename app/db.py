import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

from sqlalchemy import BigInteger, Text, DateTime, String, func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from logger import logger

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

class PersonaLore(Base):
    __tablename__ = "persona_lore"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 384 - Size of FastEmbed vector (BAAI/bge-small-en-v1.5)
    embedding: Mapped[List[float]] = mapped_column(Vector(384), nullable=False)

class UserFact(Base):
    __tablename__ = "user_facts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    fact: Mapped[str] = mapped_column(Text, nullable=False)
    # 384 - Size of FastEmbed vector (BAAI/bge-small-en-v1.5)
    embedding: Mapped[List[float]] = mapped_column(Vector(384), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

async def init_db():
    try:
        logger.debug("Initializing database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}", exc_info=True)
        raise

async def add_message(chat_id: int, role: str, content: str):
    try:
        async with AsyncSessionLocal() as session:
            msg = Message(chat_id=chat_id, role=role, content=content)
            session.add(msg)
            await session.commit()
            logger.debug(f"Saved message to DB | chat_id={chat_id}, role={role}, len={len(content)}")
    except Exception as e:
        logger.error(f"Failed to save message | chat_id={chat_id}, role={role}: {e}", exc_info=True)

async def get_recent_history(chat_id: int, limit: int = 10) -> List[Dict[str, str]]:
    try:
        async with AsyncSessionLocal() as session:
            get_messages_by_limit_query = (
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.id.desc())
                .limit(limit)
            )
            result = await session.execute(get_messages_by_limit_query)
            messages = result.scalars().all()
            messages.reverse()
            
            logger.debug(f"Fetched {len(messages)} history messages for chat_id={chat_id}")
            return [{"role": msg.role, "content": msg.content} for msg in messages]
    except Exception as e:
        logger.error(f"Failed to fetch history for chat_id={chat_id}: {e}", exc_info=True)
        return []

async def add_lore_to_db(content: str, category: str, embedding: list[float]) -> bool:
    try:
        async with AsyncSessionLocal() as session:
            lore_entry = PersonaLore(
                category=category,
                content=content,
                embedding=embedding
            )
            session.add(lore_entry)
            await session.commit()
            logger.info(f"Saved new persona lore | category={category}, content='{content[:30]}...'")
            return True
    except Exception as e:
        logger.error(f"Failed to save persona lore: {e}", exc_info=True)
        return False

async def add_user_fact(chat_id: int, fact: str, embedding: List[float]) -> bool:
    try:
        async with AsyncSessionLocal() as session:
            fact_entry = UserFact(chat_id=chat_id, fact=fact, embedding=embedding)
            session.add(fact_entry)
            await session.commit()
            logger.debug(f"Saved user fact | chat_id={chat_id}, fact='{fact}'")
            return True
    except Exception as e:
        logger.error(f"Failed to save user fact for chat_id={chat_id}: {e}", exc_info=True)
        return False

async def get_relevant_user_facts(chat_id: int, query_embedding: List[float], limit: int = 3, threshold: float = 0.55) -> List[str]:
    try:
        async with AsyncSessionLocal() as session:
            user_facts_query = (
                select(UserFact.fact)
                .where(UserFact.chat_id == chat_id)
                .where(UserFact.embedding.cosine_distance(query_embedding) < threshold)
                .order_by(UserFact.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            result = await session.execute(user_facts_query)
            facts = list(result.scalars().all())
            logger.debug(f"RAG UserFacts retrieved | chat_id={chat_id}, count={len(facts)}")
            return facts
    except Exception as e:
        print(f"[DB_Error] Couldn't fetch user facts: {e}")
        return []