"""Script to create the default admin user.

Reads ADMIN_USERNAME and ADMIN_PASSWORD from .env / environment.

Usage:
    cd backend
    .venv/bin/python create_user.py
"""

import asyncio

from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models.user import User
from app.services.auth import hash_password


async def main() -> None:
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    if password in ("changeme", ""):
        print("WARNING: Set ADMIN_USERNAME and ADMIN_PASSWORD in your .env before running this script.")
        return

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            print(f"User '{username}' already exists.")
            return

        user = User(
            username=username,
            hashed_password=hash_password(password),
        )
        db.add(user)
        await db.commit()
        print(f"User '{username}' created successfully.")


if __name__ == "__main__":
    asyncio.run(main())
