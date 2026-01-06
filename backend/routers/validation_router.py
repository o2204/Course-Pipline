from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(
    prefix="/validate",
    tags=["Validation"]
)


@router.post("/storyboard")
async def validate_storyboard(payload: Dict[str, Any]):
    errors: List[str] = []

    # ---------- Root ----------
    if payload.get("result") != "success":
        errors.append("Field 'result' must be 'success'")

    data = payload.get("data")
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="'data' must be a list")

    # ---------- Videos ----------
    for v_index, video in enumerate(data, start=1):
        shots = video.get("shots")

        if not isinstance(shots, list):
            errors.append(f"Video {v_index}: 'shots' must be a list")
            continue

        if len(shots) != 4:
            errors.append(
                f"Video {v_index}: expected 4 shots, found {len(shots)}"
            )

        # ---------- Shots ----------
        for s_index, shot in enumerate(shots, start=1):
            frames = shot.get("frames")

            if not isinstance(frames, list):
                errors.append(
                    f"Video {v_index}, Shot {s_index}: 'frames' must be a list"
                )
                continue

            if len(frames) != 3:
                errors.append(
                    f"Video {v_index}, Shot {s_index}: expected 3 frames, found {len(frames)}"
                )

            # ---------- Frames ----------
            for f_index, frame in enumerate(frames, start=1):
                if "frame_number" not in frame:
                    errors.append(
                        f"Video {v_index}, Shot {s_index}, Frame {f_index}: missing 'frame_number'"
                    )

                if "frame_code" not in frame:
                    errors.append(
                        f"Video {v_index}, Shot {s_index}, Frame {f_index}: missing 'frame_code'"
                    )

                if not isinstance(frame.get("frame_prompt"), dict):
                    errors.append(
                        f"Video {v_index}, Shot {s_index}, Frame {f_index}: 'frame_prompt' must be an object"
                    )

    if errors:
        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "message": "Storyboard JSON output is valid"
    }
