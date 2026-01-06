# backend/repo/image_repo.py

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.image import Image


class ImageRepository:
    """Repository for Images table operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_image(
        self,
        course_name: str,
        frame_code: str,
        image_url: str,
        request_id: Optional[str] = None
    ) -> Image:
        """
        Create a new image record.
        
        Args:
            course_name: Course identifier
            frame_code: Frame identifier (e.g., "V1_S2_F3")
            image_url: URL to generated image
            request_id: Optional Higgsfield request ID
            
        Returns:
            Created Image instance
            
        Raises:
            IntegrityError: If (course_name, frame_code) already exists
        """
        image = Image(
            course_name=course_name,
            frame_code=frame_code,
            image_url=image_url,
            request_id=request_id
        )
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image
    
    async def get_by_frame_code(
        self,
        course_name: str,
        frame_code: str
    ) -> Optional[Image]:
        """
        Get image by course_name and frame_code.
        
        Args:
            course_name: Course identifier
            frame_code: Frame identifier
            
        Returns:
            Image instance or None
        """
        result = await self.db.execute(
            select(Image).where(
                Image.course_name == course_name,
                Image.frame_code == frame_code
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_course(self, course_name: str) -> List[Image]:
        """
        Get all images for a course.
        
        Args:
            course_name: Course identifier
            
        Returns:
            List of Image instances
        """
        result = await self.db.execute(
            select(Image).where(Image.course_name == course_name)
        )
        return list(result.scalars().all())
    
    async def exists(self, course_name: str, frame_code: str) -> bool:
        """
        Check if image exists for frame.
        
        Args:
            course_name: Course identifier
            frame_code: Frame identifier
            
        Returns:
            True if exists, False otherwise
        """
        image = await self.get_by_frame_code(course_name, frame_code)
        return image is not None
    
    async def update_image_url(
        self,
        course_name: str,
        frame_code: str,
        image_url: str
    ) -> Optional[Image]:
        """
        Update image URL for a frame.
        
        Args:
            course_name: Course identifier
            frame_code: Frame identifier
            image_url: New image URL
            
        Returns:
            Updated Image instance or None if not found
        """
        image = await self.get_by_frame_code(course_name, frame_code)
        if image:
            image.image_url = image_url
            await self.db.commit()
            await self.db.refresh(image)
        return image
    
    async def delete_by_frame_code(
        self,
        course_name: str,
        frame_code: str
    ) -> bool:
        """
        Delete image by frame_code.
        
        Args:
            course_name: Course identifier
            frame_code: Frame identifier
            
        Returns:
            True if deleted, False if not found
        """
        image = await self.get_by_frame_code(course_name, frame_code)
        if image:
            await self.db.delete(image)
            await self.db.commit()
            return True
        return False
    
    async def delete_all_by_course(self, course_name: str) -> int:
        """
        Delete all images for a course.
        
        Args:
            course_name: Course identifier
            
        Returns:
            Number of images deleted
        """
        images = await self.get_all_by_course(course_name)
        count = len(images)
        for image in images:
            await self.db.delete(image)
        await self.db.commit()
        return count
    async def get_urls_by_course_name(
        self,
        course_name: str
    ) -> list[dict]:
        """
        Get all image URLs for a course.

        Args:
            course_name: Course identifier

        Returns:
            List of dicts: [{frame_code, image_url}]
        """
        result = await self.db.execute(
            select(
                Image.frame_code,
                Image.image_url
            ).where(
                Image.course_name == course_name
            ).order_by(Image.frame_code)
        )

        rows = result.all()

        return [
            {
                "frame_code": frame_code,
                "image_url": image_url
            }
            for frame_code, image_url in rows
        ]

