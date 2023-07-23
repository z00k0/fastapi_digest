from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import uvicorn
from models import Base
from schemas import DigestSchema, DigestPostSchema
from utils import populate_db, get_digest, generate_digest, update_digest
from scanner import SQLitePostScanner
from filters import popularity_filter


app = FastAPI(title="Digest API")

DB_URL = "sqlite+aiosqlite:///digest.db"
engine = create_async_engine(DB_URL, echo=True)
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# database = databases.Database(DB_URL)
# Base.metadata.create_all(engine)
scanner = SQLitePostScanner()


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.get("/api/populate-db")
async def populate(session: AsyncSession = Depends(get_session)):
    await populate_db(session)

    return {"message": "DB successfully populated"}


@app.get("/api/user/{user_id}/digest", response_model=DigestSchema)
async def create_digest(
    user_id: int,
    worker: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    rating: int | None = 0,
    count: int | None = 3,
):
    posts = await scanner.scan(session, user_id=user_id)
    if rating is not None:
        posts = popularity_filter(posts, min_popularity=rating)
    if count:
        posts = posts[:count]
    digest = await generate_digest(session, user_id)
    # upd_d = await update_digest(session, digest, posts)
    worker.add_task(update_digest, session, digest, posts)

    return digest


@app.get("/api/digest/{digest_id}", response_model=DigestPostSchema)
async def get_digest_by_id(
    digest_id: int, session: AsyncSession = Depends(get_session)
):
    return await get_digest(session, digest_id=digest_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)
