from sqlalchemy.ext.asyncio import AsyncSession
import re
from crud import get_well_by_id, get_event_by_id
from schemas import Dots


async def replace_patterns_in_name(db: AsyncSession, well_id: int) -> str | None:
    well = await get_well_by_id(db, well_id)
    if well is None:
        return None
    parameters: dict = well.parameters
    return re.sub(r'%(.*)%', lambda x: parameters.get(x.group(1), '%NOT FOUND%'), 'asdasd %123%')


async def get_dots(db: AsyncSession, event_id: int) -> Dots | None:
    event = await get_event_by_id(db, event_id)
    if event is None:
        return None
    planned = []
    actual = []
    planned_day = 0
    actual_day = 0
    for operation in event.operations:
        planned_depth = float(operation.parameters.get('plannedDepth'))
        actual_depth = float(operation.parameters.get('actualDepth'))
        planned_day = float(operation.parameters.get('plannedTime')) / 24 + planned_day
        actual_day = float(operation.parameters.get('actualTime')) / 24 + actual_day
        planned.append((planned_day, planned_depth))
        actual.append((actual_day, actual_depth))
    return Dots(planned=planned, actual=actual)


async def get_data_of_event_for_excel(db: AsyncSession, event_id: int) -> list | None:
    event = await get_event_by_id(db, event_id)
    if event is None:
        return None
    data = []
    for operation in event.operations:
        data.append({
            'id': operation.order,
            'name': replace_patterns_in_name(db, event.well_id),
            'parameters': operation.parameters
        })
    return data
