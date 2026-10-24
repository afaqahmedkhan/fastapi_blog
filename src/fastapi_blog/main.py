from pathlib import Path as PathLib
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi_blog.schemas import PostCreate, PostListResponse, PostPublic
from fastapi_blog.store import (
    POST_LIMIT,
    create_post,
    find_post_by_id,
    get_post_by_id,
    home_page_posts,
    list_posts,
    list_posts_by_author,
)

PACKAGE_DIR = PathLib(__file__).resolve().parent

app = FastAPI(title="FastAPI Blog", version="0.1.0")

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


def home_context() -> dict:
    visible, has_more = home_page_posts()
    return {
        "posts": visible,
        "title": "Home",
        "limit": POST_LIMIT,
        "has_more": has_more,
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
            "title": post.title,
        },
    )


@app.get("/api/v1/posts", response_model=PostListResponse)
def get_posts(
    skip: Annotated[int, Query(ge=0, description="Number of posts to skip.")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of posts to return."),
    ] = POST_LIMIT,
) -> PostListResponse:
    return list_posts(skip=skip, limit=limit)


@app.get("/api/v1/posts/{post_id}", response_model=PostPublic)
def get_post(
    post_id: Annotated[
        int,
        Path(
            ge=1,
            title="Post ID",
            description="Numeric identifier of the blog post (must be a positive integer).",
        ),
    ],
) -> PostPublic:
    return get_post_by_id(post_id)


@app.post("/api/v1/posts", response_model=PostPublic, status_code=201)
def post_create(post_in: PostCreate) -> PostPublic:
    return create_post(post_in)


@app.get("/users/{user_id}/posts", name="user_posts", include_in_schema=False)
def user_posts(
    request: Request,
    user_id: Annotated[int, Path(ge=1, title="User ID")],
):
    user_posts_list = list_posts_by_author(user_id)
    if not user_posts_list:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": user_posts_list,
            "title": f"{user_posts_list[0].author.username}'s posts",
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
