# backend/repo/prompt_repo.py

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.prompt import Prompt


class PromptRepository:
    """
    Repository for Prompts table operations.
    
    CRITICAL: NO JSON querying in SQL - always retrieve full prompt_json 
    and use Python utilities (backend.utils.frame_extractor) for traversal.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_prompt(
        self,
        course_name: str,
        prompt_json: dict,
        model_name: str = "gpt-4o-mini"
    ) -> Prompt:
        """
        Create a new prompt record with full storyboard JSON.
        
        Args:
            course_name: Course identifier
            prompt_json: Full storyboard structure as dict (will be stored as JSONB)
            model_name: AI model used for generation
            
        Returns:
            Created Prompt instance
        """
        prompt = Prompt(
            course_name=course_name,
            prompt_json=prompt_json,
            model_name=model_name,
        )
        self.db.add(prompt)
        await self.db.commit()
        await self.db.refresh(prompt)
        return prompt
    
    async def get_by_course_name(self, course_name: str) -> Optional[Prompt]:
        """
        Get prompt by course_name.
        
        Returns the FULL prompt_json as Python dict.
        All frame extraction MUST be done in Python after retrieval.
        
        Args:
            course_name: Course identifier
            
        Returns:
            Prompt instance or None
        """
        result = await self.db.execute(
            select(Prompt).where(Prompt.course_name == course_name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        """
        Get prompt by UUID.
        
        Args:
            prompt_id: Prompt UUID
            
        Returns:
            Prompt instance or None
        """
        result = await self.db.execute(
            select(Prompt).where(Prompt.id == prompt_id)
        )
        return result.scalar_one_or_none()
    
    async def update_prompt_json(self, course_name: str, prompt_json: dict) -> Optional[Prompt]:
        """
        Update prompt_json for a course.
        
        Args:
            course_name: Course identifier
            prompt_json: Updated storyboard structure
            
        Returns:
            Updated Prompt instance or None if not found
        """
        prompt = await self.get_by_course_name(course_name)
        if prompt:
            prompt.prompt_json = prompt_json
            await self.db.commit()
            await self.db.refresh(prompt)
        return prompt
    
    async def delete_by_course_name(self, course_name: str) -> bool:
        """
        Delete prompt by course_name.
        
        Args:
            course_name: Course identifier
            
        Returns:
            True if deleted, False if not found
        """
        prompt = await self.get_by_course_name(course_name)
        if prompt:
            await self.db.delete(prompt)
            await self.db.commit()
            return True
        return False
