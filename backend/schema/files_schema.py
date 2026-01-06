from pydantic import BaseModel
from uuid import UUID
from typing import List


class FrameOut(BaseModel):
    frame_id: UUID
    frame_number: int


class ShotOut(BaseModel):
    shot_id: UUID
    shot_number: int
    frames: List[FrameOut]


class VideoOut(BaseModel):
    video_id: UUID
    video_number: int
    title: str
    shots: List[ShotOut]


class ExtractFileResponse(BaseModel):
    result: str
    file_id: UUID
    data: List[VideoOut]
