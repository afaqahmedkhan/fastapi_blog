from datetime import datetime

from fastapi import HTTPException

from fastapi_blog.schemas import (
    DEFAULT_AVATAR_PATH,
    AuthorPublic,
    PostCreate,
    PostPublic,
    PostListResponse,
)

POST_LIMIT = 10

_AUTHORS: dict[int, AuthorPublic] = {
    1: AuthorPublic(id=1, username="DadJokeMaster", image_path=DEFAULT_AVATAR_PATH),
    2: AuthorPublic(id=2, username="PunnyParent", image_path=DEFAULT_AVATAR_PATH),
    3: AuthorPublic(id=3, username="JokeGenius", image_path=DEFAULT_AVATAR_PATH),
    4: AuthorPublic(id=4, username="LaughingDad", image_path=DEFAULT_AVATAR_PATH),
    5: AuthorPublic(id=5, username="ChuckleChampion", image_path=DEFAULT_AVATAR_PATH),
    6: AuthorPublic(id=6, username="DadJokeKing", image_path=DEFAULT_AVATAR_PATH),
    7: AuthorPublic(id=7, username="GiggleGuru", image_path=DEFAULT_AVATAR_PATH),
    8: AuthorPublic(id=8, username="ComedyDad", image_path=DEFAULT_AVATAR_PATH),
    9: AuthorPublic(id=9, username="JesterDad", image_path=DEFAULT_AVATAR_PATH),
    10: AuthorPublic(id=10, username="FunnyFather", image_path=DEFAULT_AVATAR_PATH),
}

_SEED_POSTS: list[tuple[int, int, str, str, datetime]] = [
    (1, 1, "Why don’t skeletons fight each other?", "They don’t have the guts!", datetime(2026, 9, 17)),
    (2, 2, "What do you call a fake noodle?", "An impasta!", datetime(2026, 9, 16)),
    (3, 3, "Why did the scarecrow win an award?", "Because he was outstanding in his field!", datetime(2026, 9, 15)),
    (4, 4, "What’s brown and sticky?", "A stick!", datetime(2026, 9, 14)),
    (5, 5, "How do you organize a space party?", "You planet!", datetime(2026, 9, 13)),
    (6, 6, "Why can’t you trust an atom?", "Because they make up everything!", datetime(2026, 9, 12)),
    (7, 7, "What’s the best time to go to the dentist?", "Tooth-hurty! (2:30)", datetime(2026, 9, 11)),
    (8, 8, "Why did the bicycle fall over?", "Because it was two-tired!", datetime(2026, 9, 10)),
    (9, 9, "What do you call cheese that isn’t yours?", "Nacho cheese!", datetime(2026, 9, 9)),
    (10, 10, "Why did the math book look sad?", "Because it had too many problems!", datetime(2026, 9, 8)),
]

_posts: list[PostPublic] = [
    PostPublic(
        id=post_id,
        title=title,
        content=content,
        author=_AUTHORS[author_id],
        date_posted=date_posted,
    )
    for post_id, author_id, title, content, date_posted in _SEED_POSTS
]

_next_post_id = max(p.id for p in _posts) + 1


def _get_author(author_id: int) -> AuthorPublic:
    author = _AUTHORS.get(author_id)
    if author is None:
        raise HTTPException(
            status_code=404,
            detail=f"Author with id {author_id} was not found",
        )
    return author


def find_post_by_id(post_id: int) -> PostPublic | None:
    return next((post for post in _posts if post.id == post_id), None)


def get_post_by_id(post_id: int) -> PostPublic:
    post = find_post_by_id(post_id)
    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {post_id} was not found",
        )
    return post


def list_posts(skip: int = 0, limit: int = POST_LIMIT) -> PostListResponse:
    slice_end = skip + limit
    page = _posts[skip:slice_end]
    return PostListResponse(
        posts=page,
        has_more=slice_end < len(_posts),
        skip=skip,
        limit=limit,
    )


def list_posts_by_author(user_id: int) -> list[PostPublic]:
    return [post for post in _posts if post.author.id == user_id]


def create_post(post_in: PostCreate) -> PostPublic:
    global _next_post_id

    author = _get_author(post_in.author_id)
    post = PostPublic(
        id=_next_post_id,
        title=post_in.title,
        content=post_in.content,
        author=author,
        date_posted=datetime.now(),
    )
    _next_post_id += 1
    _posts.insert(0, post)
    return post


def home_page_posts() -> tuple[list[PostPublic], bool]:
    visible = _posts[:POST_LIMIT]
    return visible, len(_posts) > POST_LIMIT
