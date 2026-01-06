# backend/schema/video_schema.py

from pydantic import BaseModel, Field
from typing import Optional


class GenerateVideoRequest(BaseModel):
    """Request schema for video generation (frontend contract)."""
    url_1: str = Field(..., description="First frame image URL (Required)")
    url_2: Optional[str] = Field(None, description="Last frame image URL (Optional, for interpolation)")
    motion_prompt: Optional[str] = Field(None, description="Custom motion prompt (Optional, backend will auto-generate if missing)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url_1": "https://storage.example.com/frame1.png",
                "url_2": "https://storage.example.com/frame10.png",
                "motion_prompt": "Camera pans left slowly"
            }
        }


class GenerateVideoResponse(BaseModel):
    """Response schema for video generation (frontend contract)."""
    video_url: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "video_url": "https://storage.example.com/video1.mp4"
            }
        }


class VideoInfoResponse(BaseModel):
    """Response schema for video information."""
    course_name: str
    video_number: int
    video_url: Optional[str] = None
    script_clean: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True
