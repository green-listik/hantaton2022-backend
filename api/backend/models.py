import os
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.orderinglist import OrderingList, ordering_list
from datetime import time
import config


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "Users"

    username: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String(60))
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    middle_name: Mapped[str | None]
    is_admin: Mapped[bool]


class Field(Base):
    __tablename__ = "Fields"

    name: Mapped[str] = mapped_column(primary_key=True)

    bushes: Mapped[list["Bush"]] = relationship(back_populates="field", lazy="joined")


class Bush(Base):
    __tablename__ = "Bushes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    field_name: Mapped[int] = mapped_column(ForeignKey("Fields.name"))

    wells: Mapped[list["Well"]] = relationship(back_populates="bush", lazy="joined")
    field: Mapped["Field"] = relationship(back_populates="bushes", lazy="joined")


class Well(Base):
    __tablename__ = "Wells"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    parameters: Mapped[dict] = mapped_column(JSON())
    bush_id: Mapped[int] = mapped_column(ForeignKey("Bushes.id"))

    events: Mapped[list["Event"]] = relationship(back_populates="well", lazy="joined")
    bush: Mapped["Bush"] = relationship(back_populates="wells", lazy="joined")


class Event(Base):
    __tablename__ = "Events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str]
    well_id: Mapped[int] = mapped_column(ForeignKey("Wells.id"))

    operations: Mapped[OrderingList["Operation"]] = relationship(collection_class=ordering_list("order", count_from=0), back_populates="event", order_by="Operation.order", lazy="joined")
    well: Mapped["Well"] = relationship(back_populates="events", lazy="joined")


class Operation(Base):
    __tablename__ = "Operations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order: Mapped[int]
    name: Mapped[str]
    parameters: Mapped[dict] = mapped_column(JSON())
    is_completed: Mapped[bool]
    event_id: Mapped[int] = mapped_column(ForeignKey("Events.id"))

    event: Mapped["Event"] = relationship(back_populates="operations", lazy="joined")


class ExampleOperation(Base):
    __tablename__ = "ExampleOperations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    parameters: Mapped[dict] = mapped_column(JSON())


engine = create_async_engine(config.DB_URL, echo=True)
async_session: async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)


async def init_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
