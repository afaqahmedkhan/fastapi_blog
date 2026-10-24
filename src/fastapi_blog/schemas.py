from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

DEFAULT_AVATAR_PATH = "/static/icons/icon.svg"

PostIdPath = Annotated[
    int,
    Field(
        ge=1,
        title="Post ID",
        description="Numeric identifier of the blog post (must be a positive integer).",
    ),
]

UserIdPath = Annotated[
    int,
    Field(
        ge=1,
        title="User ID",
        description="Numeric identifier of the author (must be a positive integer).",
    ),
]


class AuthorBase(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=50,
        description="Display name of the author.",
    )

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("username must not be empty")
        return stripped


class AuthorPublic(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    image_path: str = Field(min_length=1, max_length=500)


class PostBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Headline shown on the blog index and post page.",
    )
    content: str = Field(
        min_length=1,
        max_length=10_000,
        description="Body text of the post.",
    )

    @field_validator("title", "content")
    @classmethod
    def strip_and_require_non_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty or whitespace only")
        return stripped


class PostCreate(PostBase):
    author_id: int = Field(
        default=1,
        ge=1,
        description="ID of the author who wrote the post.",
    )


class PostPublic(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    author: AuthorPublic
    date_posted: datetime


class PostListResponse(BaseModel):
    posts: list[PostPublic]
    has_more: bool
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)


class MessageResponse(BaseModel):
    detail: str
