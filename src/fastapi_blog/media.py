import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from fastapi_blog.config import PROFILE_PICS_DIR, settings


def _extension_for_content_type(content_type: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    ext = mapping.get(content_type)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image type.",
        )
    return ext


async def save_profile_picture(user_id: int, upload: UploadFile) -> str:
    if upload.content_type not in settings.allowed_image_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile picture must be JPEG, PNG, WebP, or GIF.",
        )

    body = await upload.read()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(body) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds maximum upload size.",
        )

    extension = _extension_for_content_type(upload.content_type)
    filename = f"user_{user_id}_{secrets.token_hex(8)}{extension}"
    destination: Path = PROFILE_PICS_DIR / filename
    destination.write_bytes(body)
    return filename
