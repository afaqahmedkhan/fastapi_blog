from contextlib import asynccontextmanager
from pathlib import Path as PathLib
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Path, Query, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi_blog.config import PROFILE_PICS_DIR, settings
from fastapi_blog.crud.posts import (
    create_post as create_post_record,
    get_post,
    home_page_posts,
    list_posts,
    list_posts_by_user,
)
from fastapi_blog.crud.users import (
    create_user,
    get_user,
    get_user_by_email,
    get_user_by_username,
    list_users,
    set_user_profile_image,
)
from fastapi_blog.database import init_db
from fastapi_blog.dependencies import DbSession
from fastapi_blog.media import save_profile_picture
from fastapi_blog.schemas import (
    PostCreate,
    PostListResponse,
    PostPublic,
    UserCreate,
    UserDetail,
    UserPublic,
)
from fastapi_blog.seed import seed_database

PACKAGE_DIR = PathLib(__file__).resolve().parent

_DEFAULT_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c"
    b"\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c"
    b"\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01"
    b"\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01"
    b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"
    b"\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
    b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x14"
    b"2\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a"
    b"%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89"
    b"\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9"
    b"\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9"
    b"\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8"
    b"\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01"
    b"\x00\x00?\x00\xfb\xd5\x7f\xff\xd9"
)


def ensure_default_profile_image() -> None:
    default_path = PROFILE_PICS_DIR / "default.jpg"
    if not default_path.exists():
        default_path.write_bytes(_DEFAULT_JPEG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ensure_default_profile_image()
    from fastapi_blog.database import SessionLocal

    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

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
app.mount(
    "/media",
    StaticFiles(directory=str(settings.media_root)),
    name="media",
)


def home_context(db: DbSession) -> dict:
    posts, has_more = home_page_posts(db, settings.post_page_size)
    return {
        "posts": posts,
        "title": "Home",
        "limit": settings.post_page_size,
        "has_more": has_more,
    }


@app.get("/", name="home", include_in_schema=False)
@app.get("/post", include_in_schema=False)
def home(request: Request, db: DbSession):
    return templates.TemplateResponse(
        request,
        "home.html",
        home_context(db),
    )


@app.get("/posts/{post_id}", name="post_page", include_in_schema=False)
@app.get("/post/{post_id}", include_in_schema=False)
def post_page(
    request: Request,
    db: DbSession,
    post_id: Annotated[
        int,
        Path(
            ge=1,
            title="Post ID",
            description="Numeric identifier of the blog post (must be a positive integer).",
        ),
    ],
):
    post = get_post(db, post_id)
    if post is None:
        return post_error_response(
            request,
            status_code=404,
            heading="Post not found",
            message=f"No post exists with id {post_id}.",
        )
    post_public = PostPublic.model_validate(post)
    return templates.TemplateResponse(
        request,
        "post.html",
        {
            "post": post_public,
            "title": post_public.title,
        },
    )


@app.get("/api/v1/posts", response_model=PostListResponse)
def get_posts(
    db: DbSession,
    skip: Annotated[int, Query(ge=0, description="Number of posts to skip.")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of posts to return."),
    ] = settings.post_page_size,
) -> PostListResponse:
    return list_posts(db, skip=skip, limit=limit)


@app.get("/api/v1/posts/{post_id}", response_model=PostPublic)
def get_post_api(
    db: DbSession,
    post_id: Annotated[
        int,
        Path(
            ge=1,
            title="Post ID",
            description="Numeric identifier of the blog post (must be a positive integer).",
        ),
    ],
) -> PostPublic:
    post = get_post(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} was not found",
        )
    return PostPublic.model_validate(post)


@app.post("/api/v1/posts", response_model=PostPublic, status_code=status.HTTP_201_CREATED)
def post_create(post_in: PostCreate, db: DbSession) -> PostPublic:
    return create_post_record(db, post_in)


@app.get("/api/v1/users", response_model=list[UserPublic])
def get_users(
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[UserPublic]:
    users = list_users(db, skip=skip, limit=limit)
    return [UserPublic.model_validate(user) for user in users]


@app.post("/api/v1/users", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: DbSession) -> UserDetail:
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    user = create_user(db, user_in)
    return UserDetail.model_validate(user)


@app.get("/api/v1/users/{user_id}", response_model=UserDetail)
def get_user_api(
    db: DbSession,
    user_id: Annotated[int, Path(ge=1, title="User ID")],
) -> UserDetail:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} was not found",
        )
    return UserDetail.model_validate(user)


@app.post(
    "/api/v1/users/{user_id}/profile-picture",
    response_model=UserPublic,
)
async def upload_profile_picture(
    db: DbSession,
    user_id: Annotated[int, Path(ge=1, title="User ID")],
    file: Annotated[UploadFile, File(description="Profile image file")],
) -> UserPublic:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} was not found",
        )
    filename = await save_profile_picture(user_id, file)
    user = set_user_profile_image(db, user, filename)
    return UserPublic.model_validate(user)


@app.get("/users/{user_id}/posts", name="user_posts", include_in_schema=False)
def user_posts(
    request: Request,
    db: DbSession,
    user_id: Annotated[int, Path(ge=1, title="User ID")],
):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_posts_list = list_posts_by_user(db, user_id)
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": user_posts_list,
            "title": f"{user.username}'s posts",
            "limit": settings.post_page_size,
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
