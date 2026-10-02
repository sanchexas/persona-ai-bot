import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

from sqlalchemy import BigInteger, Text, DateTime, String, func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from pgvector.sqlalchemy import Vector

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
    # 1536 - vector size for OpenAI / OpenRouter models
    embedding: Mapped[List[float]] = mapped_column(Vector(1536), nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_message(chat_id: int, role: str, content: str):
    async with AsyncSessionLocal() as session:
        msg = Message(chat_id=chat_id, role=role, content=content)
        session.add(msg)
        await session.commit()

async def get_recent_history(chat_id: int, limit: int = 10) -> List[Dict[str, str]]:
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
        
        return [{"role": msg.role, "content": msg.content} for msg in messages]

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
            return True
    except Exception as e:
        print(f"[DB Error] Couldn't save lore entry: {e}")
        return False