import asyncio
from uuid import UUID

from backend.repo.frame_repo import FrameRepository
from backend.repo.generation_job_repo import GenerationJobRepository
from backend.clients.higgsfield_client import HiggsFieldClient
from backend.clients.supabase_storage import upload_image_to_supabase


async def poll_image_generation(
    db,
    job_id: UUID,
    frame_id: UUID,
    request_id: str,
):
    job_repo = GenerationJobRepository(db)
    frame_repo = FrameRepository(db)
    higgs_client = HiggsFieldClient()

    try:
        while True:
            status, image_bytes = await higgs_client.get_status(
                request_id=request_id
            )

            if status == "running":
                await asyncio.sleep(3)
                continue

            if status == "failed":
                await job_repo.update_status(
                    job_id=job_id,
                    status="failed",
                    error="Higgs generation failed",
                )
                await frame_repo.update_status(
                    frame_id=frame_id,
                    status="failed",
                )
                return

            if status == "completed":
                # Upload image
                image_url = await upload_image_to_supabase(
                    image_bytes=image_bytes,
                    file_id=frame_id,
                    video_number=1,
                    shot_number=1,
                    frame_code="",
                )

                await frame_repo.update_status(
                    frame_id=frame_id,
                    status="completed",
                    image_url=image_url,
                )

                await job_repo.update_status(
                    job_id=job_id,
                    status="completed",
                )
                return

            await asyncio.sleep(3)

    except Exception as e:
        await job_repo.update_status(
            job_id=job_id,
            status="failed",
            error=str(e),
        )
        await frame_repo.update_status(
            frame_id=frame_id,
            status="failed",
        )
