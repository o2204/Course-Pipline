"""
Frame Extraction Utilities

CRITICAL RULE: All JSON traversal must happen in Python, NOT in SQL.
This module provides utilities to extract frame data from the prompt_json JSONB structure.

Frame Code Format: "V{video_number}_S{shot_number}_F{frame_number}"
Example: "V1_S2_F3" = Video 1, Shot 2, Frame 3
"""

from typing import Optional, Dict, List


def parse_frame_code(frame_code: str) -> tuple[int, int, int]:
    """
    Parse frame_code into video, shot, and frame numbers.
    
    Args:
        frame_code: Format "V1_S2_F3"
        
    Returns:
        Tuple of (video_number, shot_number, frame_number)
        
    Raises:
        ValueError: If frame_code format is invalid
    """
    try:
        parts = frame_code.split("_")
        if len(parts) != 3:
            raise ValueError(f"Invalid frame_code format: {frame_code}")
        
        video_num = int(parts[0][1:])  # Remove 'V' prefix
        shot_num = int(parts[1][1:])   # Remove 'S' prefix
        frame_num = int(parts[2][1:])  # Remove 'F' prefix
        
        return video_num, shot_num, frame_num
    except (IndexError, ValueError) as e:
        raise ValueError(f"Invalid frame_code format: {frame_code}. Expected format: V1_S2_F3") from e


def generate_frame_code(video_number: int, shot_number: int, frame_number: int) -> str:
    """
    Generate frame_code from video, shot, and frame numbers.
    
    Args:
        video_number: Video sequence number (1-based)
        shot_number: Shot sequence number (1-based)
        frame_number: Frame sequence number (1-based)
        
    Returns:
        Frame code in format "V1_S2_F3"
    """
    return f"V{video_number}_S{shot_number}_F{frame_number}"


def extract_frame_prompt(prompt_json: dict, frame_code: str) -> Optional[str]:
    """
    Extract frame_prompt from prompt_json using frame_code.
    
    IMPORTANT: This function performs JSON traversal in PYTHON, not SQL.
    
    Args:
        prompt_json: The full storyboard JSONB object from database
        frame_code: Frame identifier (e.g., "V1_S2_F3")
        
    Returns:
        The frame_prompt text, or None if not found
        
    Example:
        >>> prompt_json = {
        ...     "videos": [
        ...         {
        ...             "video_number": 1,
        ...             "shots": [
        ...                 {
        ...                     "shot_number": 2,
        ...                     "frames": [
        ...                         {"frame_number": 3, "frame_prompt": "A sunny beach"}
        ...                     ]
        ...                 }
        ...             ]
        ...         }
        ...     ]
        ... }
        >>> extract_frame_prompt(prompt_json, "V1_S2_F3")
        'A sunny beach'
    """
    try:
        video_num, shot_num, frame_num = parse_frame_code(frame_code)
        
        # Navigate through the JSON structure
        videos = prompt_json.get("videos", [])
        
        # Find the video (1-based indexing)
        video = None
        for v in videos:
            if v.get("video_number") == video_num:
                video = v
                break
        
        if not video:
            return None
        
        # Find the shot
        shots = video.get("shots", [])
        shot = None
        for s in shots:
            if s.get("shot_number") == shot_num:
                shot = s
                break
        
        if not shot:
            return None
        
        # Find the frame
        frames = shot.get("frames", [])
        frame = None
        for f in frames:
            if f.get("frame_number") == frame_num:
                frame = f
                break
        
        if not frame:
            return None
        
        return frame.get("frame_prompt")
        
    except ValueError:
        return None


def extract_all_frames(prompt_json: dict) -> List[Dict[str, str]]:
    """
    Extract all frames with their codes and prompts.
    
    Args:
        prompt_json: The full storyboard JSONB object from database
        
    Returns:
        List of dictionaries with frame_code and frame_prompt
        
    Example:
        >>> frames = extract_all_frames(prompt_json)
        >>> frames[0]
        {'frame_code': 'V1_S1_F1', 'frame_prompt': 'A beautiful sunset', 'video_number': 1, 'shot_number': 1, 'frame_number': 1}
    """
    frames = []
    
    videos = prompt_json.get("videos", [])
    
    for video in videos:
        video_num = video.get("video_number")
        shots = video.get("shots", [])
        
        for shot in shots:
            shot_num = shot.get("shot_number")
            shot_frames = shot.get("frames", [])
            
            for frame in shot_frames:
                frame_num = frame.get("frame_number")
                frame_prompt = frame.get("frame_prompt", "")
                
                frame_code = generate_frame_code(video_num, shot_num, frame_num)
                
                frames.append({
                    "frame_code": frame_code,
                    "frame_prompt": frame_prompt,
                    "video_number": video_num,
                    "shot_number": shot_num,
                    "frame_number": frame_num,
                })
    
    return frames


def extract_frames_for_video(prompt_json: dict, video_number: int) -> List[Dict[str, str]]:
    """
    Extract all frames for a specific video.
    
    Args:
        prompt_json: The full storyboard JSONB object from database
        video_number: The video number to extract frames from
        
    Returns:
        List of dictionaries with frame_code and frame_prompt for the specified video
        
    Example:
        >>> frames = extract_frames_for_video(prompt_json, video_number=1)
        >>> len(frames)
        15  # All frames from video 1
    """
    frames = []
    
    videos = prompt_json.get("videos", [])
    
    # Find the specific video
    target_video = None
    for video in videos:
        if video.get("video_number") == video_number:
            target_video = video
            break
    
    if not target_video:
        return frames
    
    shots = target_video.get("shots", [])
    
    for shot in shots:
        shot_num = shot.get("shot_number")
        shot_frames = shot.get("frames", [])
        
        for frame in shot_frames:
            frame_num = frame.get("frame_number")
            frame_prompt = frame.get("frame_prompt", "")
            
            frame_code = generate_frame_code(video_number, shot_num, frame_num)
            
            frames.append({
                "frame_code": frame_code,
                "frame_prompt": frame_prompt,
                "video_number": video_number,
                "shot_number": shot_num,
                "frame_number": frame_num,
            })
    
    return frames


def get_video_count(prompt_json: dict) -> int:
    """Get the number of videos in the storyboard."""
    return len(prompt_json.get("videos", []))


def get_shot_count(prompt_json: dict, video_number: int) -> int:
    """Get the number of shots in a specific video."""
    videos = prompt_json.get("videos", [])
    for video in videos:
        if video.get("video_number") == video_number:
            return len(video.get("shots", []))
    return 0


def get_frame_count(prompt_json: dict, video_number: int, shot_number: int) -> int:
    """Get the number of frames in a specific shot."""
    videos = prompt_json.get("videos", [])
    for video in videos:
        if video.get("video_number") == video_number:
            shots = video.get("shots", [])
            for shot in shots:
                if shot.get("shot_number") == shot_number:
                    return len(shot.get("frames", []))
    return 0
