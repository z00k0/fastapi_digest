from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List, Optional


class Base(DeclarativeBase):
    pass


user_tag = Table(
    "user_tag",
    Base.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("tag_id", ForeignKey("tag.id")),
)

post_tag = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", ForeignKey("post.id")),
    Column("tag_id", ForeignKey("tag.id")),
)

post_digest = Table(
    "post_digest",
    Base.metadata,
    Column("post_id", ForeignKey("post.id")),
    Column("digest_id", ForeignKey("digest.id")),
)


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    interest_tags: Mapped[List["Tag"]] = relationship(secondary=user_tag)


class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    popularity_rating: Mapped[int] = mapped_column(Integer)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscription.id"))

    tags: Mapped[List["Tag"]] = relationship(secondary=post_tag)


class Digest(Base):
    __tablename__ = "digest"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    post_list: Mapped[List["Post"]] = relationship(secondary=post_digest)
