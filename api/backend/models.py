import os
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "Users"

    username: Mapped[str] = mapped_column(String(256), primary_key=True)
    password: Mapped[str] = mapped_column(String(60))
    first_name: Mapped[str] = mapped_column(String(256))
    last_name: Mapped[str] = mapped_column(String(256))
    middle_name: Mapped[str] = mapped_column(String(256))
    is_admin: Mapped[bool] = mapped_column()


_DB_URL = os.getenv('DB_URL')
if _DB_URL is None:
    raise RuntimeError('`DB_URL` is not set')
engine = create_async_engine(_DB_URL, echo=True)
async_session: async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)


async def init_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
