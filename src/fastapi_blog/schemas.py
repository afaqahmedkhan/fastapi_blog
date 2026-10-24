from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
        description="Numeric identifier of the user (must be a positive integer).",
    ),
]


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("username must not be empty")
        return stripped


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    username: str
    image_path: str


class UserDetail(UserPublic):
    email: EmailStr


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=10_000)

    @field_validator("title", "content")
    @classmethod
    def strip_and_require_non_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty or whitespace only")
        return stripped


class PostCreate(PostBase):
    user_id: int = Field(
        default=1,
        ge=1,
        description="ID of the user who authors the post.",
    )


class PostPublic(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    author: UserPublic
    date_posted: datetime
    likes: int = Field(ge=0, default=0)


class PostListResponse(BaseModel):
    posts: list[PostPublic]
    has_more: bool
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)


class MessageResponse(BaseModel):
    detail: str
