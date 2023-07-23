from abc import ABC, abstractmethod
from typing import List
from models import User, Subscription, Post, Digest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class PostScanner(ABC):
    @abstractmethod
    async def scan(self):
        pass


class SQLitePostScanner(PostScanner):
    async def scan(self, session: AsyncSession, user_id: int) -> List[Post]:
        async with session.begin():
            posts = await session.execute(
                select(Post).join(Subscription).join(User).where(User.id == user_id)
            )
        return posts.scalars().all()
