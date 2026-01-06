# backend/schema/file_schema.py

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class UploadFileRequest(BaseModel):
    """Request schema for file upload."""
    course_name: str = Field(..., description="Unique course identifier (immutable)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024"
            }
        }


class UploadFileResponse(BaseModel):
    """Response schema for file upload."""
    course_name: str
    file_id: UUID
    message: str = "File uploaded successfully"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024",
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "File uploaded successfully"
            }
        }


class FileInfoResponse(BaseModel):
    """Response schema for file information."""
    file_id: UUID
    course_name: str
    full_text: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True
