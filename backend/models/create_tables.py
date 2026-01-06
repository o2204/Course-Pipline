import asyncio

from app.models.base import Base
from app.models import Files, Prompt, GenerationJob, Video, Shot, Frame
from app.db.database import engine


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully")


if __name__ == "__main__":
    asyncio.run(create_tables())
