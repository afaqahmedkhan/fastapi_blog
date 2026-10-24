from datetime import datetime
from pathlib import Path as PathLib
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

PACKAGE_DIR = PathLib(__file__).resolve().parent

app = FastAPI()

templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))


def post_error_response(
    request: Request,
    *,
    status_code: int,
    heading: str,
    message: str,
):
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "title": heading,
            "status_code": status_code,
            "heading": heading,
            "message": message,
        },
        status_code=status_code,
    )


def is_post_page_request(request: Request) -> bool:
    path = request.url.path
    return path.startswith("/posts/") or path.startswith("/post/")


def is_api_request(request: Request) -> bool:
    return request.url.path.startswith("/api")


def format_validation_message(exc: RequestValidationError) -> str:
    parts: list[str] = []
    for err in exc.errors():
        loc = [str(item) for item in err.get("loc", ()) if item not in ("body", "query", "path")]
        field = " → ".join(loc) if loc else "request"
        parts.append(f"{field}: {err.get('msg', 'Invalid value')}")
    return parts[0] if len(parts) == 1 else "; ".join(parts)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if is_api_request(request):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    if is_post_page_request(request):
        return post_error_response(
            request,
            status_code=422,
            heading="Invalid post ID",
            message="The post ID must be a positive whole number (for example: /posts/1 or /post/1).",
        )

    return post_error_response(
        request,
        status_code=422,
        heading="Invalid request",
        message=format_validation_message(exc),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and not is_api_request(request):
        if is_post_page_request(request):
            return post_error_response(
                request,
                status_code=404,
                heading="Post not found",
                message="We couldn't find that post. Check the URL or return to the home page.",
            )
        return post_error_response(
            request,
            status_code=404,
            heading="Page not found",
            message=str(exc.detail),
        )
    if isinstance(exc.detail, str):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


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


def find_post_by_id(post_id: int) -> dict | None:
    return next((p for p in posts if p["id"] == post_id), None)


def get_post_by_id(post_id: int) -> dict:
    post = find_post_by_id(post_id)
    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {post_id} was not found",
        )
    return post


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
@app.get("/post/{post_id}", include_in_schema=False)
def post_page(
    request: Request,
    post_id: Annotated[
        int,
        Path(
            ge=1,
            title="Post ID",
            description="Numeric identifier of the blog post (must be a positive integer).",
        ),
    ],
):
    post = find_post_by_id(post_id)
    if post is None:
        return post_error_response(
            request,
            status_code=404,
            heading="Post not found",
            message=f"No post exists with id {post_id}.",
        )
    return templates.TemplateResponse(
        request,
        "post.html",
        {
            "post": post,
            "title": post["title"],
        },
    )


@app.get("/api/v1/posts/{post_id}")
def get_post(
    post_id: Annotated[
        int,
        Path(
            ge=1,
            title="Post ID",
            description="Numeric identifier of the blog post (must be a positive integer).",
        ),
    ],
):
    return get_post_by_id(post_id)


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
