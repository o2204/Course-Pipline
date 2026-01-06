# backend/schema/image_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional


class GenerateImageRequest(BaseModel):
    """Request schema for single image generation."""
    course_name: str = Field(..., description="Course identifier")
    frame_code: str = Field(..., description="Frame identifier (e.g., V1_S2_F3)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024",
                "frame_code": "V1_S2_F3"
            }
        }


class GenerateImageResponse(BaseModel):
    """Response schema for image generation."""
    course_name: str
    frame_code: str
    image_url: str
    message: str = "Image generated successfully"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024",
                "frame_code": "V1_S2_F3",
                "image_url": "https://storage.example.com/image123.png",
                "message": "Image generated successfully"
            }
        }


class GenerateBulkImagesRequest(BaseModel):
    """Request schema for bulk image generation."""
    course_name: str = Field(..., description="Course identifier")
    video_number: Optional[int] = Field(
        None,
        description="Optional: generate images for specific video only"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024",
                "video_number": 1
            }
        }


class BulkImageStatus(BaseModel):
    """Status of a single image in bulk generation."""
    frame_code: str
    status: str  # "pending", "success", "failed"
    image_url: Optional[str] = None
    error: Optional[str] = None


class GenerateBulkImagesResponse(BaseModel):
    """Response schema for bulk image generation."""
    course_name: str
    total_frames: int
    generated: int
    failed: int
    images: List[BulkImageStatus]
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024",
                "total_frames": 10,
                "generated": 8,
                "failed": 2,
                "images": [
                    {
                        "frame_code": "V1_S1_F1",
                        "status": "success",
                        "image_url": "https://storage.example.com/image1.png"
                    },
                    {
                        "frame_code": "V1_S1_F2",
                        "status": "failed",
                        "error": "Generation timeout"
                    }
                ],
                "message": "Bulk generation completed with 2 failures"
            }
        }


class ImageInfoResponse(BaseModel):
    """Response schema for image information."""
    course_name: str
    frame_code: str
    image_url: str
    created_at: str
    
    class Config:
        from_attributes = True


class ImageState(BaseModel):
    """Simple state representation for frontend hydration."""
    frame_code: str
    image_url: str
    status: str = "completed"


class GetImagesResponse(BaseModel):
    """Response schema for fetching all images of a course."""
    course_name: str
    images: List[ImageState]
    count: int
