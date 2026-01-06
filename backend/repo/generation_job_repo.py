from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.generation_job import GenerationJob


class GenerationJobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------
    # Create job (MANDATORY for every generation)
    # -------------------------------------------------
    async def create_job(
        self,
        *,
        entity_type: str,   # "image" | "video"
        entity_id: UUID,
        provider: str,
        request_id: str | None = None,
        status: str = "pending",
    ) -> GenerationJob:
        job = GenerationJob(
            entity_type=entity_type,
            entity_id=entity_id,
            provider=provider,
            request_id=request_id,
            status=status,
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    # -------------------------------------------------
    # Get latest job for entity (SOURCE OF TRUTH)
    # -------------------------------------------------
    async def get_latest(
        self,
        *,
        entity_type: str,
        entity_id: UUID,
    ) -> GenerationJob | None:
        stmt = (
            select(GenerationJob)
            .where(
                GenerationJob.entity_type == entity_type,
                GenerationJob.entity_id == entity_id,
            )
            .order_by(GenerationJob.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    # -------------------------------------------------
    # Update job status
    # -------------------------------------------------
    async def update_status(
        self,
        *,
        job_id: UUID,
        status: str,
        error: str | None = None,
    ) -> GenerationJob | None:
        stmt = select(GenerationJob).where(GenerationJob.id == job_id)
        res = await self.db.execute(stmt)
        job = res.scalar_one_or_none()

        if not job:
            return None

        job.status = status
        if error:
            job.error = error

        await self.db.flush()
        await self.db.refresh(job)
        return job

    # -------------------------------------------------
    # Retry helpers
    # -------------------------------------------------
    async def get_retryable_jobs(self, max_retries: int) -> list[GenerationJob]:
        stmt = select(GenerationJob).where(
            GenerationJob.status == "failed",
            GenerationJob.retries < max_retries,
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def increment_retry(self, job_id: UUID) -> GenerationJob | None:
        stmt = select(GenerationJob).where(GenerationJob.id == job_id)
        res = await self.db.execute(stmt)
        job = res.scalar_one_or_none()

        if not job:
            return None

        job.retries += 1
        await self.db.flush()
        await self.db.refresh(job)
        return job
