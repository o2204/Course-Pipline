# backend/clients/openai_client.py

from typing import Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from backend.config.settings import settings


class Frame(BaseModel):
    """Frame structure in storyboard."""
    frame_number: int = Field(..., ge=1)
    frame_prompt: str = Field(..., min_length=1)


class Shot(BaseModel):
    """Shot structure containing multiple frames."""
    shot_number: int = Field(..., ge=1)
    scene_en: str = Field(..., min_length=1)
    frames: list[Frame] = Field(..., min_items=1)


class Video(BaseModel):
    """Video structure containing multiple shots."""
    video_number: int = Field(..., ge=1)
    shots: list[Shot] = Field(..., min_items=1)


class StoryboardResponse(BaseModel):
    """Full storyboard response structure."""
    videos: list[Video] = Field(..., min_items=1)


class OpenAIClient:
    """Client for OpenAI API interactions."""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_storyboard(self, full_text: str) -> Dict[str, Any]:
        """
        Generate structured storyboard from course text.
        
        Args:
            full_text: Full course text content
            
        Returns:
            Storyboard structure as dict with videos/shots/frames
        """
        system_prompt = """You are a professional video storyboard creator.
        
Given a course script, create a detailed visual storyboard with:
- Multiple videos (if the content is long)
- Each video has multiple shots (scenes)
- Each shot has multiple frames with detailed visual prompts

For each frame, generate a detailed visual description including:
- Scene composition
- Lighting and atmosphere
- Key visual elements
- Style and mood

Return a structured JSON with this format:
{
  "videos": [
    {
      "video_number": 1,
      "shots": [
        {
          "shot_number": 1,
          "scene_en": "Introduction scene",
          "frames": [
            {
              "frame_number": 1,
              "frame_prompt": "Detailed visual description..."
            }
          ]
        }
      ]
    }
  ]
}
"""
        
        user_prompt = f"Create a visual storyboard for this course content:\n\n{full_text}"
        
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=StoryboardResponse
            )
            
            # Extract parsed response
            parsed = response.choices[0].message.parsed
            return parsed.model_dump()
            
        except Exception as e:
            raise RuntimeError(f"OpenAI storyboard generation failed: {str(e)}")
    
    async def generate_clean_script(
        self,
        prompt_json: Dict[str, Any],
        video_number: int
    ) -> Optional[str]:
        """
        Generate cleaned script for a specific video.
        
        Args:
            prompt_json: Full storyboard JSON
            video_number: Video sequence number
            
        Returns:
            Cleaned script text or None
        """
        # Extract video data
        videos = prompt_json.get("videos", [])
        target_video = None
        for video in videos:
            if video.get("video_number") == video_number:
                target_video = video
                break
        
        if not target_video:
            return None
        
        system_prompt = """You are a professional script editor.
        
Given a video storyboard with shots and frames, create a clean, natural narration script.
Make it engaging and suitable for voiceover."""
        
        user_prompt = f"Create a narration script for this video:\n\n{target_video}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Return None if script generation fails (non-critical)
            return None


def get_openai_client() -> OpenAIClient:
    """Factory function to get OpenAI client instance."""
    return OpenAIClient()
