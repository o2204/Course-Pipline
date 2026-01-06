# backend/repo/file_repo.py

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.file import Files


class FileRepository:
    """Repository for Files table operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_file(self, course_name: str, full_text: str) -> Files:
        """
        Create a new file record.
        
        Args:
            course_name: Unique course identifier (immutable)
            full_text: Extracted text content from file
            
        Returns:
            Created Files instance
            
        Raises:
            IntegrityError: If course_name already exists
        """
        file = Files(
            course_name=course_name,
            full_text=full_text,
        )
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file
    
    async def get_by_course_name(self, course_name: str) -> Optional[Files]:
        """
        Get file by course_name.
        
        Args:
            course_name: Course identifier
            
        Returns:
            Files instance or None
        """
        result = await self.db.execute(
            select(Files).where(Files.course_name == course_name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, file_id: UUID) -> Optional[Files]:
        """
        Get file by UUID (for compatibility).
        
        Args:
            file_id: File UUID
            
        Returns:
            Files instance or None
        """
        result = await self.db.execute(
            select(Files).where(Files.id == file_id)
        )
        return result.scalar_one_or_none()
    
    async def exists(self, course_name: str) -> bool:
        """
        Check if course_name already exists.
        
        Args:
            course_name: Course identifier to check
            
        Returns:
            True if exists, False otherwise
        """
        file = await self.get_by_course_name(course_name)
        return file is not None
    
    async def get_active_course_name(self) -> Optional[str]:
        """
        Get the most recently created course name.
        
        Used for resolving course context when frontend doesn't provide it.
        
        Returns:
            Course name of the most recent file, or None if no files exist
        """
        result = await self.db.execute(
            select(Files).order_by(Files.created_at.desc()).limit(1)
        )
        file = result.scalar_one_or_none()
        return file.course_name if file else None
    
    async def delete_by_course_name(self, course_name: str) -> bool:
        """
        Delete file by course_name (cascades to prompts, images, videos).
        
        Args:
            course_name: Course identifier
            
        Returns:
            True if deleted, False if not found
        """
        file = await self.get_by_course_name(course_name)
        if file:
            await self.db.delete(file)
            await self.db.commit()
            return True
        return False
