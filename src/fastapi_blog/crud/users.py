from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_blog.models import User
from fastapi_blog.schemas import UserCreate
from fastapi_blog.security import hash_password


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return list(db.scalars(select(User).offset(skip).limit(limit)).all())


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username.strip(),
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_profile_image(db: Session, user: User, filename: str) -> User:
    user.image_file = filename
    db.commit()
    db.refresh(user)
    return user
