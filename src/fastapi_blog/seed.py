from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi_blog.models import Post, User
from fastapi_blog.security import hash_password

_SEED_USERS = [
    ("DadJokeMaster", "dad@example.com"),
    ("PunnyParent", "punny@example.com"),
    ("JokeGenius", "genius@example.com"),
    ("LaughingDad", "laughing@example.com"),
    ("ChuckleChampion", "champion@example.com"),
    ("DadJokeKing", "king@example.com"),
    ("GiggleGuru", "guru@example.com"),
    ("ComedyDad", "comedy@example.com"),
    ("JesterDad", "jester@example.com"),
    ("FunnyFather", "father@example.com"),
]

_SEED_POSTS = [
    ("Why don’t skeletons fight each other?", "They don’t have the guts!", 0),
    ("What do you call a fake noodle?", "An impasta!", 1),
    ("Why did the scarecrow win an award?", "Because he was outstanding in his field!", 2),
    ("What’s brown and sticky?", "A stick!", 3),
    ("How do you organize a space party?", "You planet!", 4),
    ("Why can’t you trust an atom?", "Because they make up everything!", 5),
    ("What’s the best time to go to the dentist?", "Tooth-hurty! (2:30)", 6),
    ("Why did the bicycle fall over?", "Because it was two-tired!", 7),
    ("What do you call cheese that isn’t yours?", "Nacho cheese!", 8),
    ("Why did the math book look sad?", "Because it had too many problems!", 9),
]

_SEED_DATES = [
    datetime(2026, 9, 17, tzinfo=UTC),
    datetime(2026, 9, 16, tzinfo=UTC),
    datetime(2026, 9, 15, tzinfo=UTC),
    datetime(2026, 9, 14, tzinfo=UTC),
    datetime(2026, 9, 13, tzinfo=UTC),
    datetime(2026, 9, 12, tzinfo=UTC),
    datetime(2026, 9, 11, tzinfo=UTC),
    datetime(2026, 9, 10, tzinfo=UTC),
    datetime(2026, 9, 9, tzinfo=UTC),
    datetime(2026, 9, 8, tzinfo=UTC),
]


def seed_database(db: Session) -> None:
    if (db.scalar(select(func.count()).select_from(User)) or 0) > 0:
        return

    password_hash = hash_password("changeme123")
    users: list[User] = []
    for username, email in _SEED_USERS:
        user = User(username=username, email=email, password_hash=password_hash)
        db.add(user)
        users.append(user)
    db.flush()

    for index, (title, content, user_index) in enumerate(_SEED_POSTS):
        db.add(
            Post(
                title=title,
                content=content,
                user_id=users[user_index].id,
                date_posted=_SEED_DATES[index],
            )
        )

    db.commit()
