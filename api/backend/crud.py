from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Field, Bush, Well, Event, Operation, ExampleOperation
import schemas
from security import get_hash_password
from typing import Sequence


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    res = (await db.execute(select(User).where(User.username == username))).scalars().one_or_none()
    return res


async def create_user(db: AsyncSession, user: schemas.User) -> User:
    hashed_password = get_hash_password(user.password)
    db_user = User(
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

async def get_fields(db: AsyncSession) -> Sequence[Field]:
    return (await db.execute(select(Field))).scalars().all()

async def get_field_by_name(db: AsyncSession, name: str) -> Field | None:
    return (await db.execute(select(Field).where(Field.name == name))).scalars().one_or_none()

async def get_bush_by_id(db: AsyncSession, id: int) -> Bush | None:
    return (await db.execute(select(Bush).where(Bush.id == id))).scalars().one_or_none()

async def get_well_by_id(db: AsyncSession, id: int) -> Well | None:
    return (await db.execute(select(Well).where(Well.id == id))).scalars().one_or_none()

async def get_event_by_id(db: AsyncSession, id: int) -> Event | None:
    return (await db.execute(select(Event).where(Event.id == id))).scalars().one_or_none()

async def get_operation_by_id(db: AsyncSession, id: int) -> Operation | None:
    return (await db.execute(select(Operation).where(Operation.id == id))).scalars().one_or_none()

async def get_example_operation_by_id(db: AsyncSession, id: int) -> ExampleOperation | None:
    return (await db.execute(select(ExampleOperation).where(ExampleOperation.id == id))).scalars().one_or_none()

async def get_example_operations_by_name(db: AsyncSession, name: str) -> Sequence[ExampleOperation]:
    return (await db.execute(select(ExampleOperation).where(ExampleOperation.name == name))).scalars().all()
