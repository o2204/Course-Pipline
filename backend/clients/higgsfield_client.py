# backend/clients/higgsfield_client.py

from typing import Optional, List
import httpx
from backend.config.settings import settings


class HiggsfieldClient:
    """
    Client for Higgsfield AI API interactions.
    """
    
    def __init__(self):
        # We allow missing keys for mock/testing
        self.api_key = settings.HIGGSFIELD_API_KEY
        self.api_secret = settings.HIGGSFIELD_API_SECRET
        self.base_url = settings.HIGGSFIELD_API_URL
        
        # Use platform URL but allow override
        if not self.base_url:
             self.base_url = "https://platform.higgsfield.ai"

    def _get_headers(self) -> dict:
        """Get headers with correct authentication."""
        if not self.api_key or not self.api_secret:
            return {}
        return {
            "Authorization": f"Key {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _poll_status(self, request_id: str, client: httpx.AsyncClient) -> str:
        """
        Poll request status until completion or failure.
        
        Returns:
            URL to the generated media (image or video).
        """
        max_retries = 60  # 60 * 2s = 120s max wait
        for _ in range(max_retries):
            import asyncio
            await asyncio.sleep(2)
            
            status_response = await client.get(
                f"{self.base_url}/requests/{request_id}/status",
                headers=self._get_headers(),
                timeout=10.0
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data.get("status")
            
            if status == "completed":
                # Handle images
                images = status_data.get("images", [])
                if images and isinstance(images, list):
                    return images[0].get("url")
                
                # Handle video
                video = status_data.get("video", {})
                if video and video.get("url"):
                    return video.get("url")

                # Fallback to result object if structure differs
                result_url = status_data.get("result", {}).get("images", [None])[0] or status_data.get("image_url")
                if result_url:
                     return result_url

                raise RuntimeError(f"Completed status but no media URL found: {status_data}")
            
            elif status in ["failed", "canceled", "error", "nsfw"]:
                error_msg = status_data.get("error", "Unknown error")
                raise RuntimeError(f"Higgsfield status is {status}: {error_msg}")
        
        raise RuntimeError("Generation timed out")

    async def generate_image(self, frame_prompt: str) -> dict:
        """
        Generate image from frame prompt using Higgsfield API.
        Returns dict with 'url' and 'request_id'.
        """
        if not frame_prompt:
            raise ValueError("frame_prompt cannot be empty")
        
        # Mock Mode
        if not self.api_key or not self.api_secret or "your_" in self.api_key:
            print("Using Mock Higgsfield Client (Invalid/Missing API Credentials)")
            return {
                "url": f"https://placehold.co/1024x576/png?text={frame_prompt[:20]}",
                "request_id": "mock_request_id"
            }

        try:
            async with httpx.AsyncClient() as client:
                # Submit to configured image model
                submit_url = f"{self.base_url}/{settings.HIGGSFIELD_IMAGE_MODEL_ID}"
                
                payload = {
                    "prompt": frame_prompt,
                    "aspect_ratio": "16:9",
                    "resolution": "720p" # Good default
                }
                
                response = await client.post(
                    submit_url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                request_id = data.get("request_id")
                
                if not request_id:
                    raise RuntimeError("No request_id returned from Higgsfield")
                
                # Poll for result
                image_url = await self._poll_status(request_id, client)
                
                return {
                    "url": image_url,
                    "request_id": request_id
                }
                
        except httpx.HTTPError as e:
            raise RuntimeError(f"Higgsfield API connection error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Higgsfield generation error: {str(e)}")

    async def generate_video(
        self,
        prompt: str,
        first_frame_image: Optional[str] = None,
        last_frame_image: Optional[str] = None,
        duration: int = 5
    ) -> dict:
        """
        Generate video using Higgsfield API (DOP/Image-to-Video).
        
        Args:
           prompt: Motion prompt (script)
           first_frame_image: URL of the first frame (REQUIRED for DOP)
           last_frame_image: URL of the last frame (REQUIRED for DOP)
           duration: Video duration in seconds
            
        Returns:
            Dict containing:
            - 'url': URL to generated video
            - 'request_id': Higgsfield request ID
        """
        if not prompt:
             raise ValueError("prompt cannot be empty")

        # Mock Mode
        if not self.api_key or not self.api_secret or "your_" in self.api_key:
             print("Using Mock Higgsfield Client for Video")
             return {
                 "url": "https://placehold.co/video/placeholder.mp4",
                 "request_id": "mock_video_request"
             }

        try:
            async with httpx.AsyncClient() as client:
                # Use DOP model by default if images provided
                # Default: higgsfield-ai/dop/standard
                if not getattr(settings, "HIGGSFIELD_DOP_MODEL_ID", None):
                     model_id = "higgsfield-ai/dop/standard"
                else:
                     model_id = settings.HIGGSFIELD_DOP_MODEL_ID

                submit_url = f"{self.base_url}/{model_id}"
                
                # Payload for DOP:
                # {
                #   "image_url": "first_frame_url",
                #   "prompt": "motion prompt (last frame included implicitly/explicitly via prompt text if needed, but API usually takes one image + prompt)",
                #   "duration": 5
                # }
                # NOTE: The User Request specified passing first_frame_image and last_frame_imageLogic.
                # However, the user also mentioned: "DOP interface uses single image_url (first), last frame implicit/in prompt or payload if supported"
                # Updated per specific instruction: 
                # "Payload: { 'image_url': <first>, 'prompt': <motion>, 'duration': 5 }"
                
                if not first_frame_image:
                    raise ValueError("first_frame_image is required for DOP video generation")

                payload = {
                    "image_url": first_frame_image,
                    "prompt": prompt,
                    "duration": duration
                }
                
                # If last_frame_image is relevant to API, we might need to add it, but user instructed strict payload match.
                # We will trust the user's specification for the Payload structure.

                response = await client.post(
                    submit_url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                request_id = data.get("request_id")
                
                if not request_id:
                    raise RuntimeError("No request_id returned from Higgsfield Video API")
                
                # Poll for result
                video_url = await self._poll_status(request_id, client)
                
                return {
                    "url": video_url,
                    "request_id": request_id
                }

        except httpx.HTTPError as e:
            raise RuntimeError(f"Higgsfield Video API connection error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Higgsfield video generation error: {str(e)}")


def get_higgsfield_client() -> HiggsfieldClient:
    """Factory function to get Higgsfield client instance."""
    return HiggsfieldClient()
