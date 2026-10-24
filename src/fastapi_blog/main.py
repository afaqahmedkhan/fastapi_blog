from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

PACKAGE_DIR = Path(__file__).resolve().parent

app = FastAPI()

templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))

app.mount(
    "/static",
    StaticFiles(directory=str(PACKAGE_DIR / "static")),
    name="static",
)

POST_LIMIT = 10

posts = [
    {
        "id": 1,
        "author": {
            "id": 1,
            "username": "DadJokeMaster",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "Why don’t skeletons fight each other?",
        "content": "They don’t have the guts!",
        "date_posted": datetime(2026, 9, 17),
    },
    {
        "id": 2,
        "author": {
            "id": 2,
            "username": "PunnyParent",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "What do you call a fake noodle?",
        "content": "An impasta!",
        "date_posted": datetime(2026, 9, 16),
    },
    {
        "id": 3,
        "author": {
            "id": 3,
            "username": "JokeGenius",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "Why did the scarecrow win an award?",
        "content": "Because he was outstanding in his field!",
        "date_posted": datetime(2026, 9, 15),
    },
    {
        "id": 4,
        "author": {
            "id": 4,
            "username": "LaughingDad",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "What’s brown and sticky?",
        "content": "A stick!",
        "date_posted": datetime(2026, 9, 14),
    },
    {
        "id": 5,
        "author": {
            "id": 5,
            "username": "ChuckleChampion",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "How do you organize a space party?",
        "content": "You planet!",
        "date_posted": datetime(2026, 9, 13),
    },
    {
        "id": 6,
        "author": {
            "id": 6,
            "username": "DadJokeKing",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "Why can’t you trust an atom?",
        "content": "Because they make up everything!",
        "date_posted": datetime(2026, 9, 12),
    },
    {
        "id": 7,
        "author": {
            "id": 7,
            "username": "GiggleGuru",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "What’s the best time to go to the dentist?",
        "content": "Tooth-hurty! (2:30)",
        "date_posted": datetime(2026, 9, 11),
    },
    {
        "id": 8,
        "author": {
            "id": 8,
            "username": "ComedyDad",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "Why did the bicycle fall over?",
        "content": "Because it was two-tired!",
        "date_posted": datetime(2026, 9, 10),
    },
    {
        "id": 9,
        "author": {
            "id": 9,
            "username": "JesterDad",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "What do you call cheese that isn’t yours?",
        "content": "Nacho cheese!",
        "date_posted": datetime(2026, 9, 9),
    },
    {
        "id": 10,
        "author": {
            "id": 10,
            "username": "FunnyFather",
            "image_path": "/static/icons/icon.svg",
        },
        "title": "Why did the math book look sad?",
        "content": "Because it had too many problems!",
        "date_posted": datetime(2026, 9, 8),
    },
]


def home_context():
    visible = posts[:POST_LIMIT]
    return {
        "posts": visible,
        "title": "Home",
        "limit": POST_LIMIT,
        "has_more": len(posts) > POST_LIMIT,
    }


@app.get("/", name="home", include_in_schema=False)
@app.get("/post", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        home_context(),
    )


@app.get("/posts/{post_id}", name="post_page", include_in_schema=False)
def post_page(post_id: int, request: Request):
    post = next((p for p in posts if p["id"] == post_id), None)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": [post],
            "title": post["title"],
            "limit": POST_LIMIT,
            "has_more": False,
        },
    )


@app.get("/users/{user_id}/posts", name="user_posts", include_in_schema=False)
def user_posts(user_id: int, request: Request):
    user_posts_list = [p for p in posts if p["author"]["id"] == user_id]
    if not user_posts_list:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": user_posts_list,
            "title": f"{user_posts_list[0]['author']['username']}'s posts",
            "limit": POST_LIMIT,
            "has_more": False,
        },
    )


@app.get("/login", name="login_page", include_in_schema=False)
def login_page():
    return HTMLResponse("<!doctype html><title>Login</title><p>Login — not implemented yet.</p>")


@app.get("/register", name="register_page", include_in_schema=False)
def register_page():
    return HTMLResponse(
        "<!doctype html><title>Register</title><p>Register — not implemented yet.</p>"
    )


@app.get("/account", name="account_page", include_in_schema=False)
def account_page():
    return HTMLResponse(
        "<!doctype html><title>Account</title><p>Account — not implemented yet.</p>"
    )


@app.get("/api/v1/posts")
def get_posts():
    return posts
