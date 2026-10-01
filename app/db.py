import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

from sqlalchemy import BigInteger, Text, DateTime, func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
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