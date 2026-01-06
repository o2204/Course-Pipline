# backend/service/prompt_service.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repo.file_repo import FileRepository
from backend.repo.prompt_repo import PromptRepository
from backend.clients.openai_client import OpenAIClient
from backend.schema.prompt_schema import GeneratePromptResponse


async def generate_prompts_service(
    course_name: str,
    db: AsyncSession
) -> GeneratePromptResponse:
    """
    Generate storyboard prompts using OpenAI.
    
    Process:
    1. Fetch full_text from files table
    2. Send to OpenAI for storyboard generation
    3 Save ENTIRE response as JSONB (no normalization)
    4. Return prompt_json
    
    Args:
        course_name: Course identifier
        db: Database session
        
    Returns:
        GeneratePromptResponse with full prompt_json
        
    Raises:
        HTTPException: If course not found or generation fails
    """
    file_repo = FileRepository(db)
    prompt_repo = PromptRepository(db)
    
    # 1. Fetch full_text
    file_obj = await file_repo.get_by_course_name(course_name)
    if not file_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Course '{course_name}' not found. Please upload a file first."
        )
    
    if not file_obj.full_text:
        raise HTTPException(
            status_code=400,
            detail=f"No text content found for course '{course_name}'"
        )
    
    # 2. Generate prompts using OpenAI
    try:
        openai_client = OpenAIClient()
        prompt_json = await openai_client.generate_storyboard(file_obj.full_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating prompts: {str(e)}"
        )
    
    # 3. Save as JSONB (entire structure, no normalization)
    try:
        prompt = await prompt_repo.create_prompt(
            course_name=course_name,
            prompt_json=prompt_json,
            model_name="gpt-4o-mini"  # Can be configured
        )
        
        return GeneratePromptResponse(
            course_name=prompt.course_name,
            prompt_json=prompt.prompt_json,
            model_name=prompt.model_name,
            success=True,
            message="Storyboard prompts generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving prompts: {str(e)}"
        )


async def get_prompts_by_course_name(
    course_name: str,
    db: AsyncSession
):
    """
    Get prompts by course_name.
    
    Returns the full prompt_json for client-side rendering.
    """
    prompt_repo = PromptRepository(db)
    prompt = await prompt_repo.get_by_course_name(course_name)
    
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail=f"No prompts found for course '{course_name}'. Generate prompts first."
        )
    
    return prompt
