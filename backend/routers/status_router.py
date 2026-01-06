from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.repo.generation_job_repo import GenerationJobRepository

router = APIRouter(prefix="/generation", tags=["status"])


@router.get("/images/{frame_id}/status")
async def get_image_status(
    frame_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = GenerationJobRepository(db)
    job = await repo.get_latest(
        entity_type="image",
        entity_id=frame_id,
    )

    if not job:
        raise HTTPException(404, "No generation job found")

    return {
        "job_id": str(job.id),
        "status": job.status,
        "error": job.error,
        "retries": job.retries,
    }


@router.get("/status/{job_id}")
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = GenerationJobRepository(db)
    job = await repo.get_by_id(job_id)

    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "entity_type": job.entity_type,
        "entity_id": str(job.entity_id),
        "status": job.status,
        "error": job.error,
        "retries": job.retries,
    }
