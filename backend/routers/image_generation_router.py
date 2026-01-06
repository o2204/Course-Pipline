# backend/routers/image_generation_router.py

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.service.image_generation_service import (
    generate_single_image_service,
    generate_bulk_images_service
)
from backend.schema.image_schema import (
    GenerateImageRequest,
    GenerateImageResponse,
    GenerateBulkImagesRequest,
    GenerateBulkImagesResponse,
    GetImagesResponse
)


router = APIRouter(prefix="/images", tags=["Image Generation"])


@router.post("/generate", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a single image for a specific frame.
    
    Process:
    1. Load prompt_json from database
    2. Extract frame_prompt using Python (NOT SQL)
    3. Send frame_prompt to Higgsfield AI
    4. Save image_url to images table
    
    Input:
        - course_name: Course identifier (required)
        - frame_code: Frame identifier like "V1_S2_F3" (required)
        
    Returns:
        - course_name: The course identifier
        - frame_code: The frame identifier
        - image_url: URL to generated image
        
    Raises:
        - 404: Course or frame not found
        - 500: Image generation or database error
        
    Example:
        POST /images/generate
        {
          "course_name": "python_basics_2024",
          "frame_code": "V1_S2_F3"
        }
    """
    return await generate_single_image_service(
        request.course_name,
        request.frame_code,
        db
    )


@router.get("/{course_name}", response_model=GetImagesResponse)
async def get_images(
    course_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all generated images for a course.
    """
    from backend.service.image_generation_service import get_course_images
    return await get_course_images(course_name, db)


@router.post("/generate/bulk", response_model=GenerateBulkImagesResponse)
async def generate_bulk_images(
    request: GenerateBulkImagesRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate images for all frames (or specific video).
    
    Process:
    1. Load prompt_json from database
    2. Extract ALL frames using Python utilities
    3. Generate images for each frame (skip if exists)
    4. Save all images with frame_codes
    
    Input:
        - course_name: Course identifier (required)
        - video_number: Optional - generate only for specific video
        
    Returns:
        - course_name: The course identifier
        - total_frames: Total number of frames processed
        - generated: Number of successfully generated images
        - failed: Number of failed generations
        - images: List of frame statuses with URLs
        
    Raises:
        - 404: Course not found or no frames in storyboard
        - 500: Image generation errors (partial)
        
    Example:
        POST /images/generate/bulk
        {
          "course_name": "python_basics_2024",
          "video_number": 1
        }
        
        Or generate for all videos:
        {
          "course_name": "python_basics_2024"
        }
    """
    return await generate_bulk_images_service(
        request.course_name,
        db,
        request.video_number
    )
