from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import random

# import requests
from typing import List
from models import User, Subscription, Post, Digest
from scanner import SQLitePostScanner
from filters import popularity_filter

scanner = SQLitePostScanner()


async def populate_db(
    session: AsyncSession, users: int = 10, subscriptions: int = 50, posts: int = 100
):
    user_list = [{"name": f"User_{n:03d}"} for n in range(1, users + 1)]

    async with session.begin():
        user_ids = await session.scalars(insert(User).returning(User.id), user_list)
        user_id_list = user_ids.all()
        subscription_list = [
            {
                "channel": f"Channel_{n:03d}",
                "user_id": random.choice(user_id_list),
            }
            for n in range(1, subscriptions + 1)
        ]
        subscription_ids = await session.scalars(
            insert(Subscription).returning(Subscription.id), subscription_list
        )
        subscription_id_list = subscription_ids.all()
        post_list = [
            {
                "content": f"Content_{n:03d}",
                "summary": f"Summary_{n:03d}",
                "popularity_rating": random.randint(-10, 10),
                "subscription_id": random.choice(subscription_id_list),
            }
            for n in range(1, posts + 1)
        ]
        post_ids = await session.execute(insert(Post), post_list)

    return user_ids


async def generate_digest(session: AsyncSession, user_id: int) -> Digest:
    async with session.begin():
        digest = await session.scalars(
            insert(Digest).returning(Digest),
            {"user_id": user_id},
        )

    return digest.first()


async def update_digest(
    session: AsyncSession, user_id: int, digest: Digest, rating: int, count: int
):
    posts = await scanner.scan(session, user_id=user_id)
    if rating is not None:
        posts = popularity_filter(posts, min_popularity=rating)
    sorted_posts = sorted(posts, key=lambda post: post.popularity_rating, reverse=True)
    if count:
        sorted_posts = sorted_posts[:count]
    async with session.begin():
        digest = await session.scalars(
            select(Digest)
            .where(Digest.id == digest.id)
            .options(selectinload(Digest.post_list))
        )
        digest = digest.first()
        digest.post_list.extend(sorted_posts)


async def get_digest(session: AsyncSession, digest_id: int):
    async with session.begin():
        digest = await session.execute(
            select(Digest)
            .where(Digest.id == digest_id)
            .options(selectinload(Digest.post_list))
        )

    return digest.scalars().first()
