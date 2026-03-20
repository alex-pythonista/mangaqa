import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
from sqlalchemy import text

from app.config import settings
from app.database import async_session, engine
from app.routers import auth, chapters, health, jobs, projects
from app.services.auth import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: check DB but don't crash if unavailable
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connected")
    except Exception as e:
        logger.warning("Database not available — %s", e)

    yield

    # Shutdown: dispose connection pool
    await engine.dispose()


app = FastAPI(title="MangaQA", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public routes
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])

# Protected routes — require JWT auth
app.include_router(projects.router, prefix="/api", tags=["projects"], dependencies=[Depends(get_current_user)])
app.include_router(chapters.router, prefix="/api", tags=["chapters"], dependencies=[Depends(get_current_user)])
app.include_router(jobs.router, prefix="/api", tags=["jobs"], dependencies=[Depends(get_current_user)])
