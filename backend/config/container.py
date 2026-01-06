from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from backend.db.database import get_db

from backend.repo.file_repo import FileRepository
from backend.repo.prompt_repo import PromptRepository
from backend.repo.generation_repo import GenerationRepository
from backend.repo.higgs_repo import HiggsRepository

from backend.service.ai_service import AgentService
from backend.service.higgs_service import HiggsService


# --------------------------------------------------
# Repository providers
# --------------------------------------------------

def get_file_repo(db: AsyncSession = Depends(get_db)) -> FileRepository:
    return FileRepository(db)


def get_prompt_repo(db: AsyncSession = Depends(get_db)) -> PromptRepository:
    return PromptRepository(db)


def get_generation_repo(db: AsyncSession = Depends(get_db)) -> GenerationRepository:
    return GenerationRepository(db)


def get_higgs_repo(db: AsyncSession = Depends(get_db)) -> HiggsRepository:
    return HiggsRepository(db)


# --------------------------------------------------
# Service providers
# --------------------------------------------------

def get_agent_service(
    db: AsyncSession = Depends(get_db),
    file_repo: FileRepository = Depends(get_file_repo),
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
) -> AgentService:
    return AgentService(
        db=db,
        file_repo=file_repo,
        prompt_repo=prompt_repo,
    )


def get_higgs_service(
    db: AsyncSession = Depends(get_db),
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    higgs_repo: HiggsRepository = Depends(get_higgs_repo),
    generation_repo: GenerationRepository = Depends(get_generation_repo),
) -> HiggsService:
    return HiggsService(
        db=db,
        prompt_repo=prompt_repo,
        higgs_repo=higgs_repo,
        generation_repo=generation_repo,
    )
