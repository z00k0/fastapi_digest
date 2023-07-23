from pydantic import BaseModel
from typing import List


class DigestSchema(BaseModel):
    id: int
    user_id: int


class PostSchema(BaseModel):
    id: int
    content: str
    summary: str
    popularity_rating: int
    subscription_id: int


class DigestPostSchema(BaseModel):
    id: int
    user_id: int
    post_list: List[PostSchema]
