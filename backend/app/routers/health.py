from fastapi import APIRouter
from sqlalchemy import text

from app.database import async_session

router = APIRouter()


@router.head("/health")
@router.get("/health")
async def health_check():
    db_status = "ok"
    db_error = None

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    return {
        "backend": "ok",
        "database": db_status,
        "database_error": db_error,
    }
