from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Field, Bush, Well, Event, Operation, ExampleOperation
import schemas
from security import get_hash_password
from typing import Sequence


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    res = (await db.execute(select(User).where(User.username == username))).scalars().unique().one_or_none()
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


async def create_field(db: AsyncSession, field: schemas.FieldBase) -> Field:
    db_field = Field(
        name=field.name
    )
    db.add(db_field)
    await db.commit()
    await db.refresh(db_field)
    return db_field


async def get_fields(db: AsyncSession) -> Sequence[Field]:
    return (await db.execute(select(Field))).scalars().unique().unique().all()


async def get_field_by_name(db: AsyncSession, name: str) -> Field | None:
    return (await db.execute(select(Field).where(Field.name == name))).scalars().unique().one_or_none()


async def create_bush(db: AsyncSession, bush: schemas.BushCreate) -> Bush | None:
    field = await get_field_by_name(db, bush.field_name)
    if field is None:
        return None
    db_bush = Bush(
        name=bush.name,
        field_name=bush.field_name
    )
    field.bushes.append(db_bush)
    db.add(db_bush)
    await db.commit()
    await db.refresh(db_bush)
    return db_bush


async def get_bush_by_id(db: AsyncSession, id: int) -> Bush | None:
    return (await db.execute(select(Bush).where(Bush.id == id))).scalars().unique().one_or_none()


async def create_well(db: AsyncSession, well: schemas.WellCreate) -> Well | None:
    bush = await get_bush_by_id(db, well.bush_id)
    if bush is None:
        return None
    db_well = Well(
        name=well.name,
        parameters=well.parameters,
        bush_id=well.bush_id,
    )
    db.add(db_well)
    bush.wells.append(db_well)
    await db.commit()
    await db.refresh(db_well)
    return db_well


async def get_well_by_id(db: AsyncSession, id: int) -> Well | None:
    return (await db.execute(select(Well).where(Well.id == id))).scalars().unique().one_or_none()


async def update_parameters_of_well(db: AsyncSession, well_id: int, new_parameters: dict) -> Well | None:
    well = await get_well_by_id(db, well_id)
    if well is None:
        return None
    well.parameters |= new_parameters
    await db.commit()
    await db.refresh(well)
    return well


async def create_event(db: AsyncSession, event: schemas.EventCreate) -> Event | None:
    well = await get_well_by_id(db, event.well_id)
    if well is None:
        return None
    db_event = Event(
        name=event.name,
        description=event.description,
        well_id=event.well_id
    )
    db.add(db_event)
    well.events.append(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event


async def get_event_by_id(db: AsyncSession, id: int) -> Event | None:
    return (await db.execute(select(Event).where(Event.id == id))).scalars().unique().one_or_none()


async def update_operation_order_for_event(db: AsyncSession, event_id: int, new_order: list[int]) -> Event | str:
    event = await get_event_by_id(db, event_id)
    if event is None:
        return "Нет такого мероприятия"
    operations_count = len(event.operations)
    are_indices_valid = True
    for i in new_order:
        if i < 0 or i >= operations_count:
            are_indices_valid = False
            break
    if len(new_order) != operations_count \
            or len(set(new_order)) != operations_count \
            or not are_indices_valid:
        return "Неверно задан порядок"
    for i in range(operations_count):
        event.operations[i].order = new_order[i]
    event.operations.reorder()
    await db.commit()
    await db.refresh(event)
    return event


async def create_operation(db: AsyncSession, operation: schemas.OperationCreate) -> Operation | None:
    event = await get_event_by_id(db, operation.event_id)
    if event is None:
        return None
    db_operation = Operation(
        name=operation.name,
        parameters=operation.parameters,
        is_complete=operation.is_complete,
        event_id=operation.event_id
    )
    db.add(db_operation)
    event.operations.append(db_operation)
    event.operations.reorder()
    await db.commit()
    await db.refresh(db_operation)
    return db_operation


async def update_parameters_of_operation(db: AsyncSession, operation_id: int, new_parameters: dict) -> Operation | None:
    operation = await get_operation_by_id(db, operation_id)
    if operation is None:
        return None
    operation.parameters |= new_parameters
    await db.commit()
    await db.refresh(operation)
    return operation


async def delete_operation(db: AsyncSession, operation_id: int) -> Event | None:
    operation = await get_operation_by_id(db, operation_id)
    if operation is None:
        return None
    event = await get_event_by_id(db, operation.event_id)
    if event is None:
        raise RuntimeError("Event not found, even though operation did? o_0")
    event.operations.pop(index=operation.order)
    event.operations.reorder()
    await db.delete(operation)
    await db.commit()
    await db.refresh(event)
    return event


async def get_operation_by_id(db: AsyncSession, id: int) -> Operation | None:
    return (await db.execute(select(Operation).where(Operation.id == id))).scalars().unique().one_or_none()


async def get_example_operation_by_id(db: AsyncSession, id: int) -> ExampleOperation | None:
    return (await db.execute(select(ExampleOperation).where(ExampleOperation.id == id))).scalars().unique().one_or_none()


async def get_example_operations_by_name(db: AsyncSession, name: str) -> Sequence[ExampleOperation]:
    return (await db.execute(select(ExampleOperation).where(ExampleOperation.name == name))).scalars().unique().all()
