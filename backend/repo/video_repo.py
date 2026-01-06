# backend/repo/video_repo.py

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.videos import Video


class VideoRepository:
    """Repository for Videos table operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_video(
        self,
        course_name: str,
        video_number: int,
        video_url: Optional[str] = None,
        motion_prompt: Optional[str] = None,
        request_id: Optional[str] = None,
        url_1: Optional[str] = None,
        url_2: Optional[str] = None
    ) -> Video:
        """
        Create a new video record.
        
        Args:
            course_name: Course identifier
            video_number: Video sequence number
            video_url: URL to generated video (optional)
            motion_prompt: Motion prompt used for generation (optional)
            request_id: Higgsfield request ID (optional)
            url_1: First frame image URL (optional)
            url_2: Last frame image URL (optional)
            
        Returns:
            Created Video instance
            
        Raises:
            IntegrityError: If (course_name, video_number) already exists
        """
        video = Video(
            course_name=course_name,
            video_number=video_number,
            video_url=video_url,
            motion_prompt=motion_prompt,
            request_id=request_id,
            url_1=url_1,
            url_2=url_2
        )
        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)
        return video
    
    async def get_by_video_number(
        self,
        course_name: str,
        video_number: int
    ) -> Optional[Video]:
        """
        Get video by course_name and video_number.
        
        Args:
            course_name: Course identifier
            video_number: Video sequence number
            
        Returns:
            Video instance or None
        """
        result = await self.db.execute(
            select(Video).where(
                Video.course_name == course_name,
                Video.video_number == video_number
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_course(self, course_name: str) -> List[Video]:
        """
        Get all videos for a course.
        
        Args:
            course_name: Course identifier
            
        Returns:
            List of Video instances ordered by video_number
        """
        result = await self.db.execute(
            select(Video)
            .where(Video.course_name == course_name)
            .order_by(Video.video_number)
        )
        return list(result.scalars().all())
    
    async def get_next_video_number(self, course_name: str) -> int:
        """
        Get the next available video number for a course.
        
        Args:
            course_name: Course identifier
            
        Returns:
            Next video number (1 if no videos exist, otherwise max + 1)
        """
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(func.max(Video.video_number))
            .where(Video.course_name == course_name)
        )
        max_number = result.scalar()
        return 1 if max_number is None else max_number + 1
    
    async def update_video(
        self,
        course_name: str,
        video_number: int,
        video_url: Optional[str] = None,
        motion_prompt: Optional[str] = None,
        url_1: Optional[str] = None,
        url_2: Optional[str] = None
    ) -> Optional[Video]:
        """
        Update video details.
        
        Args:
            course_name: Course identifier
            video_number: Video sequence number
            video_url: New video URL (if provided)
            motion_prompt: New motion prompt (if provided)
            url_1: New first frame URL (if provided)
            url_2: New last frame URL (if provided)
            
        Returns:
            Updated Video instance or None if not found
        """
        video = await self.get_by_video_number(course_name, video_number)
        if video:
            if video_url is not None:
                video.video_url = video_url
            if motion_prompt is not None:
                video.motion_prompt = motion_prompt
            if url_1 is not None:
                video.url_1 = url_1
            if url_2 is not None:
                video.url_2 = url_2
            await self.db.commit()
            await self.db.refresh(video)
        return video
    
    async def delete_by_video_number(
        self,
        course_name: str,
        video_number: int
    ) -> bool:
        """
        Delete video by video_number.
        
        Args:
            course_name: Course identifier
            video_number: Video sequence number
            
        Returns:
            True if deleted, False if not found
        """
        video = await self.get_by_video_number(course_name, video_number)
        if video:
            await self.db.delete(video)
            await self.db.commit()
            return True
        return False
    
    async def delete_all_by_course(self, course_name: str) -> int:
        """
        Delete all videos for a course.
        
        Args:
            course_name: Course identifier
            
        Returns:
            Number of videos deleted
        """
        videos = await self.get_all_by_course(course_name)
        count = len(videos)
        for video in videos:
            await self.db.delete(video)
        await self.db.commit()
        return count
