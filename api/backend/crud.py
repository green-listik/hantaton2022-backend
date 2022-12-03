from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import models
import schemas
from security import get_hash_password


async def get_user_by_username(db: AsyncSession, username: str) -> models.User | None:
    res = (await db.execute(select(models.User).where(models.User.username == username))).scalars().one_or_none()
    return res


async def create_user(db: AsyncSession, user: schemas.User) -> models.User:
    hashed_password = get_hash_password(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        is_admin=user.is_admin
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
