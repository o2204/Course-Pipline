# backend/routers/prompt_router.py

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.service.prompt_service import generate_prompts_service, get_prompts_by_course_name
from backend.schema.prompt_schema import (
    GeneratePromptRequest,
    GeneratePromptResponse,
    PromptInfoResponse
)


router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.post("/generate", response_model=GeneratePromptResponse)
async def generate_prompts(
    request: GeneratePromptRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate storyboard prompts using OpenAI.
    
    Process:
    1. Fetch full_text from files table using course_name
    2. Send to OpenAI for storyboard generation
    3. Save ENTIRE response as JSONB (no normalization)
    4. Return full prompt_json
    
    Input:
        - course_name: Course identifier (required)
        
    Returns:
        - course_name: The course identifier
        - prompt_json: Full storyboard structure
        - model_name: AI model used
        - success: True if successful
        
    Raises:
        - 404: Course not found
        - 500: OpenAI generation or database error
        
    Note:
        The prompt_json structure is:
        {
          "videos": [
            {
              "video_number": 1,
              "shots": [
                {
                  "shot_number": 1,
                  "scene_en": "Scene description",
                  "frames": [
                    {
                      "frame_number": 1,
                      "frame_prompt": "Detailed visual description"
                    }
                  ]
                }
              ]
            }
          ]
        }
    """
    return await generate_prompts_service(request.course_name, db)


@router.get("/{course_name}", response_model=PromptInfoResponse)
async def get_prompts(
    course_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get prompts by course_name.
    
    Returns the full prompt_json for frontend rendering.
    """
    prompt = await get_prompts_by_course_name(course_name, db)
    return PromptInfoResponse(
        course_name=prompt.course_name,
        prompt_json=prompt.prompt_json,
        model_name=prompt.model_name
    )
