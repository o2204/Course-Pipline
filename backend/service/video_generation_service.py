# backend/service/video_generation_service.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.repo.prompt_repo import PromptRepository
from backend.repo.video_repo import VideoRepository
from backend.repo.file_repo import FileRepository
from backend.clients.higgsfield_client import HiggsfieldClient
from backend.utils.frame_extractor import extract_frames_for_video
from backend.schema.video_schema import GenerateVideoResponse


async def generate_video_service(
    *,
    url_1: str,
    url_2: Optional[str] = None,
    motion_prompt: Optional[str] = None,
    db: AsyncSession,
) -> GenerateVideoResponse:
    """
    Generate a video using Higgsfield Image-to-Video.

    Frontend contract:
    - Accepts: url_1 (required), url_2 (optional), motion_prompt (optional)
    - Returns: { "video_url": "..." }

    Backend responsibilities:
    - Resolve valid course_name internally (must exist in files table)
    - Auto-generate motion_prompt if missing
    - Store video metadata safely in DB
    """

    if not url_1:
        raise HTTPException(status_code=400, detail="url_1 is required")

    # Initialize repositories
    file_repo = FileRepository(db)
    video_repo = VideoRepository(db)
    prompt_repo = PromptRepository(db)

    # ------------------------------------------------------------------
    # 1. Resolve VALID course_name (FK-safe)
    # ------------------------------------------------------------------
    course_name = await file_repo.get_active_course_name()
    if not course_name:
        raise HTTPException(
            status_code=500,
            detail="No valid course_name found in files table"
        )

    # Get next video number (simple + deterministic)
    video_number = await video_repo.get_next_video_number(course_name)

    # ------------------------------------------------------------------
    # 2. Resolve motion_prompt if missing
    # ------------------------------------------------------------------
    if not motion_prompt:
        try:
            prompt_data = await prompt_repo.get_by_course_name(course_name)
            if prompt_data:
                frames = extract_frames_for_video(
                    prompt_data.prompt_json,
                    video_number
                )
                if frames:
                    motion_prompt = _build_default_motion_prompt(frames)
        except Exception:
            # Ignore and fallback
            pass

        if not motion_prompt:
            motion_prompt = (
                "Cinematic camera movement, high quality, smooth motion."
            )

    # ------------------------------------------------------------------
    # 3. Generate video using Higgsfield
    # ------------------------------------------------------------------
    try:
        higgsfield = HiggsfieldClient()

        result = await higgsfield.generate_video(
            prompt=motion_prompt,
            first_frame_image=url_1,
            last_frame_image=url_2,  # None → single-image I2V
            duration=5,
        )

        video_url: str = result["url"]
        request_id: Optional[str] = result.get("request_id")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # 4. Persist video metadata (NO FK violations)
    # ------------------------------------------------------------------
    try:
        await video_repo.create_video(
            course_name=course_name,
            video_number=video_number,
            video_url=video_url,
            motion_prompt=motion_prompt,
            request_id=request_id,
            url_1=url_1,
            url_2=url_2,
        )

        # Frontend expects ONLY video_url
        return GenerateVideoResponse(video_url=video_url)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error saving video: {str(e)}"
        )


def _build_default_motion_prompt(frames_list: list) -> str:
    """
    Build a cinematic motion prompt describing transition BETWEEN frames.
    """
    if len(frames_list) < 2:
        return "Cinematic camera movement, high quality, smooth motion."

    prompt_parts = [
        "The video begins from the first frame and gradually transitions toward the final frame.",
    ]

    if len(frames_list) > 2:
        prompt_parts.append(
            "As the sequence progresses, the scene evolves through intermediate moments "
            "with smooth visual continuity."
        )

    prompt_parts.extend([
        "The camera movement is smooth and cinematic throughout.",
        "Lighting and atmosphere shift progressively to reinforce temporal continuity.",
        "The motion resolves seamlessly into the final frame.",
        "Smooth interpolation, realistic motion, stable composition, high visual coherence.",
    ])

    return " ".join(prompt_parts)
