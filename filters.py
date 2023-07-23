from typing import List
from models import Post


def popularity_filter(posts: List[Post], min_popularity: int = 0) -> List[Post]:
    return [Post for Post in posts if Post.popularity_rating > min_popularity]
