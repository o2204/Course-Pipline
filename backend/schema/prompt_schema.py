# backend/schema/prompt_schema.py

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Any


class GeneratePromptRequest(BaseModel):
    """Request schema for prompt generation."""
    course_name: str = Field(..., description="Course identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024"
            }
        }


class GeneratePromptResponse(BaseModel):
    """Response schema for prompt generation."""
    course_name: str
    prompt_json: Dict[str, Any]
    model_name: str
    success: bool = True
    message: str = "Prompts generated successfully"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "course_name": "python_basics_2024",
                "prompt_json": {
                    "videos": [
                        {
                            "video_number": 1,
                            "shots": [
                                {
                                    "shot_number": 1,
                                    "frames": [
                                        {
                                            "frame_number": 1,
                                            "frame_prompt": "A beautiful sunset over mountains"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "model_name": "gpt-4o-mini",
                "success": True,
                "message": "Prompts generated successfully"
            }
        }


class PromptInfoResponse(BaseModel):
    """Response schema for prompt information."""
    course_name: str
    prompt_json: Dict[str, Any]
    model_name: str
    
    class Config:
        from_attributes = True
