from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from fastapi_blog.models import Post, User
from fastapi_blog.schemas import PostCreate, PostListResponse, PostPublic


def _post_query():
    return select(Post).options(joinedload(Post.author))


def get_post(db: Session, post_id: int) -> Post | None:
    return db.scalar(_post_query().where(Post.id == post_id))


def list_posts(db: Session, skip: int = 0, limit: int = 10) -> PostListResponse:
    total = db.scalar(select(func.count()).select_from(Post)) or 0
    posts = list(
        db.scalars(
            _post_query().order_by(Post.date_posted.desc()).offset(skip).limit(limit)
        ).all()
    )
    return PostListResponse(
        posts=[PostPublic.model_validate(post) for post in posts],
        has_more=skip + len(posts) < total,
        skip=skip,
        limit=limit,
    )


def list_posts_by_user(db: Session, user_id: int) -> list[PostPublic]:
    posts = list(
        db.scalars(
            _post_query()
            .where(Post.user_id == user_id)
            .order_by(Post.date_posted.desc())
        ).all()
    )
    return [PostPublic.model_validate(post) for post in posts]


def create_post(db: Session, post_in: PostCreate) -> PostPublic:
    author = db.get(User, post_in.user_id)
    if author is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"User with id {post_in.user_id} was not found",
        )

    post = Post(
        title=post_in.title,
        content=post_in.content,
        user_id=post_in.user_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    post = get_post(db, post.id)
    assert post is not None
    return PostPublic.model_validate(post)


def home_page_posts(db: Session, limit: int) -> tuple[list[PostPublic], bool]:
    result = list_posts(db, skip=0, limit=limit)
    return result.posts, result.has_more
