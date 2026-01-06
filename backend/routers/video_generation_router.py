# backend/routers/video_generation_router.py

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.service.video_generation_service import generate_video_service
from backend.schema.video_schema import GenerateVideoRequest, GenerateVideoResponse


router = APIRouter(prefix="/videos", tags=["Video Generation"])


@router.post("/generate", response_model=GenerateVideoResponse)
async def generate_video(
    request: GenerateVideoRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate video from image frame(s) using Higgsfield AI.
    
    Process:
    1. Accept first frame URL (required) and optional last frame URL
    2. Auto-generate motion prompt if not provided by user
    3. Generate video using Higgsfield (I2V or I2V + End Frame)
    4. Store in database with internal course context
    5. Return video URL
    
    Input (from frontend):
        - url_1: First frame image URL (required)
        - url_2: Last frame image URL (optional, for interpolation)
        - motion_prompt: Custom motion prompt (optional, auto-generated if missing)
        
    Returns:
        - video_url: URL to generated video
        
    Raises:
        - 500: Video generation or database error
        
    Example Request:
        POST /videos/generate
        {
          "url_1": "https://storage.example.com/frame1.png",
          "url_2": "https://storage.example.com/frame10.png",
          "motion_prompt": "Camera pans right slowly"
        }
        
    Example Response:
        {
          "video_url": "https://storage.example.com/video.mp4"
        }
        
    Note:
        - If url_2 is omitted, generates video from single image (I2V).
        - If url_2 is provided, generates transition video (I2V + End Frame).
        - Motion prompt is auto-generated if not provided.
        - Course context is managed internally by backend.
    """
    return await generate_video_service(
        url_1=request.url_1,
        url_2=request.url_2,
        motion_prompt=request.motion_prompt,
        db=db
    )


@router.get("/{course_name}", response_model=list[GenerateVideoResponse])
async def get_videos(
    course_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all generated videos for a course.
    """
    from backend.repo.video_repo import VideoRepository
    repo = VideoRepository(db)
    return await repo.get_all_by_course(course_name)
