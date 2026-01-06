import os
from supabase import create_client

from backend.config.settings import settings

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
# User requested "assets" bucket
SUPABASE_BUCKET_IMAGES = os.getenv("SUPABASE_BUCKET_IMAGES", "assets")

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
else:
    supabase = None


def upload_image_to_supabase(
    *,
    file_id: str,
    video_number: int,
    shot_number: int,
    frame_code: str,
    image_bytes: bytes,
) -> tuple[str, str]:
    """
    Upload image bytes to Supabase Storage
    """

    # Example path:
    # files/{file_id}/video_1/shot_2/V1S2F3.png
    bucket_path = (
        f"files/{file_id}/"
        f"video_{video_number}/"
        f"shot_{shot_number}/"
        f"{frame_code}.png"
    )

    supabase.storage.from_(SUPABASE_BUCKET_IMAGES).upload(
        bucket_path,
        image_bytes,
        file_options={
            "content-type": "image/png",
            "upsert": True,
        },
    )

    public_url = (
        supabase.storage
        .from_(SUPABASE_BUCKET_IMAGES)
        .get_public_url(bucket_path)
    )

    return bucket_path, public_url


def upload_video_to_supabase(
    *,
    file_id: str,
    video_number: int,
    video_path: str,
) -> tuple[str, str]:
    """
    Upload video file to Supabase Storage (using the same assets bucket)
    """

    bucket_path = f"files/{file_id}/video_{video_number}/output.mp4"

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    supabase.storage.from_(SUPABASE_BUCKET_IMAGES).upload(
        bucket_path,
        video_bytes,
        file_options={
            "content-type": "video/mp4",
            "upsert": True,
        },
    )

    public_url = (
        supabase.storage
        .from_(SUPABASE_BUCKET_IMAGES)
        .get_public_url(bucket_path)
    )

    return bucket_path, public_url
